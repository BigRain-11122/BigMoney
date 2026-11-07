"""E515 -- a guarded call site is not a property of the callee.

E512 (results/state_tilt/CALLEERETURN-2026-11-07.json) published one callee
(``card_config_ticket``) whose three sites were all safe only because a terminating guard sat
between the call and the read.  Three guarded sites are evidence about three call sites, not
about the callee: the fourth site, or the next caller written tomorrow, inherits nothing.

So this face stops starting from a published row list and instead takes the *callee* as the
population: every module-level function in the corpus that returns both a nothing value (bare
``return`` or ``return None``) and a value.  For every call site of every such callee it
publishes three independent facts, which is what makes a "guarded sibling" non-evidence:

  * does a terminating guard filter the empty arm between the call and the first read;
  * does the result reach a subscript with no such guard in between;
  * is the site reachable from production code at all, or only from a selftest/entry point.

Nothing is executed and nothing is rewritten; this is a static read of the tree.

    python scripts/e515_empty_arm_cover.py run        # build + write the face
    python scripts/e515_empty_arm_cover.py check      # gate the published face
    python scripts/e515_empty_arm_cover.py verify     # re-derive and gate in memory
    python scripts/e515_empty_arm_cover.py selftest   # fixture arms + doctored arms
"""
from __future__ import annotations

import ast
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E515-DO-THE-OTHER-CALLERS-OF-A-BRANCHING-CALLEE-GUARD-THE-EMPTY-ARM"
STUDY = "E515_empty_arm_cover"
DATE_STAMP = "2026-11-08"
FACE_NAME = "emptyarmcover_latest.json"
DATED_PREFIX = "EMPTYARMCOVER"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e515_", "run_e515", "_e515", "_r1546", "EMPTYARMCOVER", "emptyarmcover_")
CORPUS_DIRS = ("scripts", "Tools", "monitor", "live", "firm", "engine", "content")
CORPUS_ROOT_FILES = ("smoke_test.py",)
SKIP_PARTS = ("__pycache__", ".git", ".codely-cli", "_quarantine", "node_modules")

TEST_FUNCS = ("selftest", "_selftest")
ENTRY_FUNCS = ("main", "_main")

RT_NOTHING = "names_nothing"
RT_VALUE = "names_a_value"
RETURN_KIND_VOCAB = (RT_NOTHING, RT_VALUE)

REACH_MODULE = "runs_at_module_level"
REACH_PRODUCTION = "inside_a_function_production_code_calls"
REACH_TEST_ONLY = "inside_a_function_only_a_test_or_entry_point_calls"
REACH_ORPHAN = "inside_a_function_nothing_in_the_corpus_calls"
REACH_VOCAB = (REACH_MODULE, REACH_PRODUCTION, REACH_TEST_ONLY, REACH_ORPHAN)

READ_SUBSCRIPT = "subscripted"
READ_ATTRIBUTE = "attribute_read"
READ_METHOD = "method_call_on_the_result"
READ_TRUTH = "truth_tested_only"
READ_HANDON = "passed_onward_or_returned"
READ_NONE = "never_read_again"
READ_VOCAB = (READ_SUBSCRIPT, READ_ATTRIBUTE, READ_METHOD, READ_TRUTH, READ_HANDON, READ_NONE)

S_GUARDED = "a_terminating_guard_filters_the_empty_arm_before_the_read"
S_TEST_ONLY = "the_result_is_read_only_from_a_test_or_entry_point"
S_UNREACHABLE = "no_corpus_caller_reaches_the_site"
S_UNGUARDED_SUBSCRIPT = "the_result_is_subscripted_with_no_guard_between"
S_UNGUARDED_OTHER = "the_result_is_read_in_production_with_no_guard_between"
S_HANDON = "the_result_is_handed_onward_without_being_read_here"
S_NEVER_READ = "the_result_is_never_read_again"
SITE_VOCAB = (S_GUARDED, S_TEST_ONLY, S_UNREACHABLE, S_UNGUARDED_SUBSCRIPT,
              S_UNGUARDED_OTHER, S_HANDON, S_NEVER_READ)

V_ALL = "every_production_site_of_a_branching_callee_filters_the_empty_arm"
V_SOME = "some_production_site_reads_the_empty_arm_unguarded"
V_NOPROD = "no_branching_callee_is_called_from_production_code"
V_EMPTY = "the_corpus_holds_no_branching_callee"
VERDICT_VOCAB = (V_ALL, V_SOME, V_NOPROD, V_EMPTY)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _src(rel, root=None):
    with io.open(os.path.join(root or ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _excerpt(node):
    try:
        text = ast.unparse(node)
    except Exception:
        return ""
    return text if len(text) <= 120 else text[:117] + "..."


# ------------------------------------------------------------------ corpus
def corpus(root=None):
    root = root or ROOT
    rels = []
    for d in CORPUS_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames
                           if x not in SKIP_PARTS and not x.startswith(".")]
            for name in filenames:
                if not name.endswith(".py") or name.startswith(SELF_EXCLUDED):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
                rels.append(rel)
    for name in CORPUS_ROOT_FILES:
        if os.path.isfile(os.path.join(root, name)) and not name.startswith(SELF_EXCLUDED):
            rels.append(name)
    return sorted(set(rels))


def parse_corpus(root=None):
    """[(rel, tree)] plus the parse failures, counted not hidden."""
    trees, failed = [], []
    for rel in corpus(root):
        try:
            trees.append((rel, ast.parse(_src(rel, root))))
        except (SyntaxError, OSError, UnicodeDecodeError, ValueError):
            failed.append(rel)
    return trees, failed


# ------------------------------------------------------------------ callee census
def return_kinds(func):
    kinds = []
    for node in ast.walk(func):
        if isinstance(node, ast.Return):
            value = node.value
            if value is None or (isinstance(value, ast.Constant) and value.value is None):
                kinds.append(RT_NOTHING)
            else:
                kinds.append(RT_VALUE)
    return kinds


def branching_callees(trees):
    """Module-level functions that name nothing on some path and a value on another."""
    out = {}
    for rel, tree in trees:
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            kinds = return_kinds(node)
            if RT_NOTHING in kinds and RT_VALUE in kinds:
                out[(rel, node.name)] = {
                    "rel": rel,
                    "name": node.name,
                    "line": node.lineno,
                    "return_paths": len(kinds),
                    "returns_nothing": kinds.count(RT_NOTHING),
                    "returns_a_value": kinds.count(RT_VALUE),
                    "parameters": [a.arg for a in list(node.args.args) + list(node.args.kwonlyargs)],
                }
    return out


def module_index(trees):
    """Leaf module name -> rel, plus dotted name -> rel for package imports."""
    index = {}
    for rel, _tree in trees:
        stem = rel[:-3] if rel.endswith(".py") else rel
        leaf = stem.split("/")[-1]
        index.setdefault(leaf, rel)
        parts = stem.split("/")
        if len(parts) > 1:
            index.setdefault(".".join(parts), rel)
            index.setdefault(".".join(parts[-2:]), rel)
        index.setdefault(stem.replace("/", "."), rel)
    return index


def resolve_call(imports, call, rel, index, callees):
    """The (rel, name) a call names, when it names one of the branching callees."""
    bare, alias = imports
    func = call.func
    if isinstance(func, ast.Name):
        name = func.id
        if (rel, name) in callees:
            return rel, name
        module_name = bare.get(name)
        if not module_name:
            return None
        target = index.get(module_name) or index.get(module_name.split(".")[-1])
        if target and (target, name) in callees:
            return target, name
        return None
    if isinstance(func, ast.Attribute):
        if not isinstance(func.value, ast.Name):
            return None
        module_name = alias.get(func.value.id)
        if not module_name:
            return None
        target = index.get(module_name) or index.get(module_name.split(".")[-1])
        if target and (target, func.attr) in callees:
            return target, func.attr
        return None
    return None


# ------------------------------------------------------------------ site analysis
def function_spans(tree):
    """[(start, end, node)] for every def, sorted; lookup is a small linear scan."""
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            spans.append((node.lineno, getattr(node, "end_lineno", node.lineno), node))
    spans.sort(key=lambda s: (s[0], -s[1]))
    return spans


def enclosing_def(spans, line):
    best = None
    for start, end, node in spans:
        if start > line:
            break
        if line <= end and (best is None or node.lineno >= best.lineno):
            best = node
    return best


def import_maps(tree):
    """Bound-name -> module for both ``from X import name`` and ``import X as alias``."""
    bare, alias = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                bare[a.asname or a.name] = node.module
        elif isinstance(node, ast.Import):
            for a in node.names:
                alias[a.asname or a.name.split(".")[0]] = a.name
    return bare, alias


def parent_map(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def call_bindings(func, call, parents):
    """What the call's result is bound to: ('name', sym) / ('returned', None) / ..."""
    node = call
    while node in parents:
        parent = parents[node]
        if isinstance(parent, ast.Assign) and parent.value is node:
            targets = [t for t in parent.targets if isinstance(t, ast.Name)]
            if len(targets) == 1:
                return "a_single_name", targets[0].id, parent
            return "an_unpacked_or_tuple_target", None, parent
        if isinstance(parent, ast.Return):
            return "the_return_value", None, parent
        if isinstance(parent, ast.Expr):
            return "discarded", None, parent
        if isinstance(parent, (ast.If, ast.While)):
            return "the_test", None, parent
        if isinstance(parent, ast.Compare):
            return "a_comparison_operand", None, parent
        if isinstance(parent, ast.Subscript) or isinstance(parent, ast.Attribute):
            return "read_in_place", None, parent
        if isinstance(parent, ast.Call):
            return "an_argument_to_another_call", None, parent
        if isinstance(parent, (ast.List, ast.Tuple, ast.Dict, ast.Set)):
            return "a_container_element", None, parent
        if isinstance(parent, ast.keyword):
            node = parent
            continue
        if isinstance(parent, (ast.BoolOp, ast.UnaryOp)):
            return "a_boolean_operand", None, parent
        return "something_else", None, parent
    return "something_else", None, None


def terminating_guards(func, start_line, end_line, symbol, ifs=None):
    """If-statements between the call and the read that terminate one arm."""
    hits = []
    if func is None or not symbol:
        return hits
    if ifs is None:
        ifs = sorted([n for n in ast.walk(func) if isinstance(n, ast.If)], key=lambda n: n.lineno)
    for node in ifs:
        if not (start_line < node.lineno <= end_line):
            continue
        names = {n.id for n in ast.walk(node.test) if isinstance(n, ast.Name)}
        if symbol not in names:
            continue
        terminates = any(isinstance(sub, (ast.Return, ast.Raise, ast.Continue, ast.Break))
                         for arm in (node.body, node.orelse) for stmt in arm
                         for sub in ast.walk(stmt))
        hints_none = ("None" in _excerpt(node.test)
                      or any(isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not)
                             for n in ast.walk(node.test)))
        hits.append({"line": node.lineno, "test": _excerpt(node.test),
                     "terminates": bool(terminates), "tests_for_nothing": bool(hints_none)})
    return sorted(hits, key=lambda g: g["line"])


def read_kind(node, parents):
    parent = parents.get(node)
    if isinstance(parent, ast.Subscript) and parent.value is node:
        return READ_SUBSCRIPT
    if isinstance(parent, ast.Attribute) and parent.value is node:
        # ``result.get(...)`` is a method call, not an attribute read
        grand = parents.get(parent)
        if isinstance(grand, ast.Call) and grand.func is parent:
            return READ_METHOD
        return READ_ATTRIBUTE
    if isinstance(parent, (ast.If, ast.While)) and parent.test is node:
        return READ_TRUTH
    if isinstance(parent, ast.UnaryOp):
        return READ_TRUTH
    if isinstance(parent, (ast.Return, ast.Call, ast.List, ast.Tuple, ast.Dict, ast.Set, ast.keyword)):
        return READ_HANDON
    return READ_HANDON


def first_reads(func, call_line, symbol, loads=None):
    if func is None or not symbol:
        return []
    if loads is None:
        loads = [n for n in ast.walk(func)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)]
    hits = [n for n in loads if n.id == symbol and n.lineno > call_line]
    return sorted(hits, key=lambda n: (n.lineno, n.col_offset))


def reach_of(func, called_from, test_calls):
    if func is None:
        return REACH_MODULE
    name = func.name
    if name in TEST_FUNCS or name.startswith("test_"):
        return REACH_TEST_ONLY
    if name in ENTRY_FUNCS:
        return REACH_PRODUCTION
    if called_from.get(name, 0) > 0:
        return REACH_PRODUCTION
    if test_calls.get(name, 0) > 0:
        return REACH_TEST_ONLY
    return REACH_ORPHAN


def call_index(trees):
    """How many times each simple name is called, split production vs test callers."""
    production, test = {}, {}
    for rel, tree in trees:
        spans = function_spans(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            else:
                continue
            owner = enclosing_def(spans, node.lineno)
            owner_name = owner.name if owner is not None else ""
            if owner_name in TEST_FUNCS or owner_name.startswith("test_"):
                test[name] = test.get(name, 0) + 1
            else:
                production[name] = production.get(name, 0) + 1
    return production, test


def site_verdict(record):
    if record["guard_terminates_before_the_read"]:
        return S_GUARDED
    if record["reach"] == REACH_TEST_ONLY:
        return S_TEST_ONLY
    if record["reach"] == REACH_ORPHAN:
        return S_UNREACHABLE
    if record["read_kind"] == READ_SUBSCRIPT:
        return S_UNGUARDED_SUBSCRIPT
    if record["read_kind"] == READ_NONE:
        return S_NEVER_READ
    if record["read_kind"] == READ_HANDON:
        return S_HANDON
    return S_UNGUARDED_OTHER


def analyse(root=None):
    root = root or ROOT
    trees, failed = parse_corpus(root)
    callees = branching_callees(trees)
    index = module_index(trees)
    production_calls, test_calls = call_index(trees)
    sites = []
    for rel, tree in trees:
        spans = function_spans(tree)
        parents = parent_map(tree)
        imports = import_maps(tree)
        func_loads, func_ifs = {}, {}
        for call in [n for n in ast.walk(tree) if isinstance(n, ast.Call)]:
            resolved = resolve_call(imports, call, rel, index, callees)
            if resolved is None:
                continue
            callee = callees[resolved]
            func = enclosing_def(spans, call.lineno)
            key = id(func)
            if key not in func_loads:
                func_loads[key] = [n for n in ast.walk(func)
                                   if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)] \
                    if func is not None else []
                func_ifs[key] = sorted([n for n in ast.walk(func) if isinstance(n, ast.If)],
                                       key=lambda n: n.lineno) if func is not None else []
            binding, symbol, bind_node = call_bindings(func, call, parents)
            reads = first_reads(func, call.lineno, symbol, func_loads[key]) if symbol else []
            if reads:
                first = reads[0]
                read_line = first.lineno
                kind = read_kind(first, parents)
                read_expression = _excerpt(parents.get(first, first))
            else:
                read_line = call.lineno
                kind = READ_NONE
                read_expression = ""
            guards = terminating_guards(func, call.lineno, read_line, symbol, func_ifs[key])
            covering = [g for g in guards if g["terminates"]]
            record = {
                "source": rel,
                "line": call.lineno,
                "call_expression": _excerpt(call),
                "callee_rel": callee["rel"],
                "callee": callee["name"],
                "callee_line": callee["line"],
                "callee_return_paths": callee["return_paths"],
                "callee_returns_nothing": callee["returns_nothing"],
                "callee_returns_a_value": callee["returns_a_value"],
                "enclosing_function": func.name if func is not None else None,
                "reach": reach_of(func, production_calls, test_calls),
                "binding": binding,
                "bound_name": symbol,
                "read_kind": kind,
                "first_read_line": read_line,
                "first_read_expression": read_expression,
                "guards_between": guards,
                "guard_terminates_before_the_read": bool(covering),
                "guard_tests_for_nothing": bool(covering and any(g["tests_for_nothing"] for g in covering)),
                "verdict": None,
            }
            record["verdict"] = site_verdict(record)
            sites.append(record)
    sites.sort(key=lambda r: (r["callee"], r["source"], r["line"]))
    return {"sites": sites, "callees": callees, "parse_failures": failed,
            "sources": len(trees)}


def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(sites, callees, sources):
    by_visit = _count(sites, "verdict", SITE_VOCAB)
    by_reach = _count(sites, "reach", REACH_VOCAB)
    prod = [s for s in sites if s["reach"] in (REACH_PRODUCTION, REACH_MODULE)]
    prod_unguarded = [s for s in prod if s["verdict"] in (S_UNGUARDED_SUBSCRIPT, S_UNGUARDED_OTHER)]
    return {
        "sources_read": sources,
        "branching_callees": len(callees),
        "callees_called_at_least_once": len({s["callee"] for s in sites}),
        "sites": len(sites),
        "sites_by_verdict": by_visit,
        "sites_by_reach": by_reach,
        "sites_by_read_kind": _count(sites, "read_kind", READ_VOCAB),
        "sites_in_production": len(prod),
        "sites_reached_only_from_a_test_or_entry": by_reach.get(REACH_TEST_ONLY, 0),
        "sites_in_a_function_nothing_calls": by_reach.get(REACH_ORPHAN, 0),
        "production_sites_that_read_the_empty_arm_unguarded": len(prod_unguarded),
        "sites_where_a_guard_filters_the_empty_arm": by_visit.get(S_GUARDED, 0),
        "sites_subscripted_without_a_guard": by_visit.get(S_UNGUARDED_SUBSCRIPT, 0),
        "sites_that_never_read_the_result": by_visit.get(S_NEVER_READ, 0),
        "sites_that_hand_the_result_onward": by_visit.get(S_HANDON, 0),
        "per_callee_site_counts": _per_callee(sites),
    }


def _per_callee(sites):
    out = {}
    for s in sites:
        key = s["callee"]
        row = out.setdefault(key, {"sites": 0, "in_production": 0, "test_only": 0,
                                   "guarded": 0, "unguarded": 0})
        row["sites"] += 1
        if s["reach"] in (REACH_PRODUCTION, REACH_MODULE):
            row["in_production"] += 1
        elif s["reach"] in (REACH_TEST_ONLY, REACH_ORPHAN):
            row["test_only"] += 1
        if s["verdict"] == S_GUARDED:
            row["guarded"] += 1
        if s["verdict"] in (S_UNGUARDED_SUBSCRIPT, S_UNGUARDED_OTHER):
            row["unguarded"] += 1
    return out


def _verdict(summary):
    if summary["sites"] == 0:
        return V_EMPTY
    if summary["sites_in_production"] == 0:
        return V_NOPROD
    if summary["production_sites_that_read_the_empty_arm_unguarded"]:
        return V_SOME
    return V_ALL


POPULATION_SOURCE = ("this study's own census: every module-level function under %s (plus %s) "
                     "that returns both a nothing value and a value, and every call site of those "
                     "functions resolved through the calling module's own import aliases"
                     % ("/".join(CORPUS_DIRS), "/".join(CORPUS_ROOT_FILES)))


def build(root=None, write=True, sites=None, callees=None, sources=None, failures=None):
    root = root or ROOT
    if sites is None:
        analysed = analyse(root)
        sites = analysed["sites"]
        callees = analysed["callees"]
        sources = analysed["sources"]
        failures = analysed["parse_failures"]
    summary = _summary(sites, callees or {}, sources or 0)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("A guarded call site is not a property of the callee.  Take every in-repo "
                  "callee that names nothing on some path and a value on another, then publish "
                  "per call site whether a terminating guard filters the empty arm, whether the "
                  "result reaches a subscript unguarded, and whether the site is reachable from "
                  "production code at all."),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "return_kind_vocab": list(RETURN_KIND_VOCAB),
        "reach_vocab": list(REACH_VOCAB),
        "read_kind_vocab": list(READ_VOCAB),
        "site_verdict_vocab": list(SITE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "callee_census": list(sorted((callees or {}).values(), key=lambda c: (-c["return_paths"], c["name"]))),
        "sites": sites,
        "summary": summary,
        "verdict": _verdict(summary),
        "parse_failures": failures or [],
        "method_limits": [
            "static only: no call is executed, so a guard that reads a different variable does not count",
            "a guard counts only when an arm of the if terminates (return/raise/continue/break)",
            "reach is a corpus fact: a function called only from selftest is reported as test-only",
            "re-exported callees and calls through computed names are not resolved and are not counted",
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
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


def load_face(root=None):
    with io.open(os.path.join(root or ROOT, "results", "state_tilt", FACE_NAME), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------- gate
def site_problems(face):
    problems = []
    sites = face.get("sites") or []
    summary = face.get("summary") or {}
    callees = face.get("callee_census") or []
    if summary.get("sites") != len(sites):
        problems.append("summary.sites is not the site list length")
    if summary.get("branching_callees") != len(callees):
        problems.append("summary.branching_callees is not the callee census length")
    if _count(sites, "verdict", SITE_VOCAB) != summary.get("sites_by_verdict"):
        problems.append("sites_by_verdict does not re-derive from the sites")
    if _count(sites, "reach", REACH_VOCAB) != summary.get("sites_by_reach"):
        problems.append("sites_by_reach does not re-derive from the sites")
    if _count(sites, "read_kind", READ_VOCAB) != summary.get("sites_by_read_kind"):
        problems.append("sites_by_read_kind does not re-derive from the sites")
    if _per_callee(sites) != summary.get("per_callee_site_counts"):
        problems.append("per_callee_site_counts does not re-derive from the sites")
    prod = [s for s in sites if s.get("reach") in (REACH_PRODUCTION, REACH_MODULE)]
    if summary.get("sites_in_production") != len(prod):
        problems.append("sites_in_production does not re-derive from the sites")
    unguarded = [s for s in prod if s.get("verdict") in (S_UNGUARDED_SUBSCRIPT, S_UNGUARDED_OTHER)]
    if summary.get("production_sites_that_read_the_empty_arm_unguarded") != len(unguarded):
        problems.append("production_sites_that_read_the_empty_arm_unguarded does not re-derive")
    for site in sites:
        if site.get("verdict") not in SITE_VOCAB:
            problems.append("verdict outside the vocabulary: %r" % (site.get("verdict"),))
        if site.get("reach") not in REACH_VOCAB:
            problems.append("reach outside the vocabulary: %r" % (site.get("reach"),))
        if site.get("read_kind") not in READ_VOCAB:
            problems.append("read kind outside the vocabulary: %r" % (site.get("read_kind"),))
        expected = site_verdict(site)
        if site.get("verdict") != expected:
            problems.append("%s:%s verdict %r is not what its own evidence implies (%r)"
                            % (site.get("source"), site.get("line"), site.get("verdict"), expected))
        if site.get("guard_terminates_before_the_read") and not site.get("guards_between"):
            problems.append("%s:%s claims a covering guard with no guard row"
                            % (site.get("source"), site.get("line")))
        if site.get("callee") not in {c.get("name") for c in callees}:
            problems.append("%s:%s names a callee outside the census: %r"
                            % (site.get("source"), site.get("line"), site.get("callee")))
    for callee in callees:
        if not (callee.get("returns_nothing") and callee.get("returns_a_value")):
            problems.append("census member %r does not return both kinds" % (callee.get("name"),))
        if callee.get("return_paths") != callee.get("returns_nothing", 0) + callee.get("returns_a_value", 0):
            problems.append("census member %r return_paths does not equal its own split"
                            % (callee.get("name"),))
    if _verdict(summary) != face.get("verdict"):
        problems.append("verdict is not what the summary implies: %r" % (face.get("verdict"),))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the vocabulary")
    if (face.get("population_source") or "") != POPULATION_SOURCE:
        problems.append("population_source was edited")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = site_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    face = build(root or ROOT, write=False)
    problems = site_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s sites=%d callees=%d"
          % (face["verdict"], len(face["sites"]), face["summary"]["branching_callees"]))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
ALPHA = '''def load(path=None):
    if path is None:
        return None
    with open(path) as fh:
        return fh.read()


def guarded(doc):
    text = load(doc)
    if text is None:
        return None
    return text["k"]


def unguarded(doc):
    text = load(doc)
    return text["k"]


def handed(doc):
    text = load(doc)
    return produce(text)


def main():
    first = guarded("x")
    second = unguarded("x")
    return first, second


def selftest():
    return guarded("x")
'''

BETA = '''import alpha


def run(doc):
    got = alpha.load(doc)
    if got is None:
        return {}
    return got["k"]


def main():
    return run("x")
'''


def _line_of(text, needle, start=0):
    """1-based line number of the first occurrence of ``needle`` at or after line ``start``."""
    lines = text.splitlines()
    for index in range(start, len(lines)):
        if needle in lines[index]:
            return index + 1
    raise AssertionError("fixture line not found: %r" % (needle,))


def selftest():
    failures = []
    checks = [0]

    def ok(label, cond, detail=None):
        checks[0] += 1
        if not cond:
            failures.append("%s (got %r)" % (label, detail))

    tmp = tempfile.mkdtemp(prefix="e515_")
    try:
        scripts = os.path.join(tmp, "scripts")
        os.makedirs(scripts)
        with io.open(os.path.join(scripts, "alpha.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(ALPHA)
        with io.open(os.path.join(scripts, "beta.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(BETA)

        face = build(tmp, write=False)
        sites = face["sites"]
        callees = {c["name"]: c for c in face["callee_census"]}
        by_key = {(s["source"], s["line"]): s for s in sites}

        guarded_line = _line_of(ALPHA, "text = load(doc)", 0)
        unguarded_line = _line_of(ALPHA, "text = load(doc)", guarded_line)
        handed_line = _line_of(ALPHA, "text = load(doc)", unguarded_line)
        test_line = _line_of(ALPHA, 'return guarded("x")', 0)
        beta_line = _line_of(BETA, "got = alpha.load(doc)", 0)

        ok("the census holds every function that names nothing on some path",
           sorted(callees) == ["guarded", "load"], sorted(callees))
        ok("the census splits its own return paths",
           callees["load"]["returns_nothing"] == 1 and callees["load"]["returns_a_value"] == 1,
           callees["load"])
        ok("six call sites are published", len(sites) == 6,
           [(s["source"], s["line"]) for s in sites])

        g = by_key.get(("scripts/alpha.py", guarded_line))
        ok("a site with a terminating None-guard is published as guarded",
           g and g["verdict"] == S_GUARDED, g and g["verdict"])
        ok("the guard row records that it terminates",
           g and g["guard_terminates_before_the_read"] and g["guards_between"][0]["terminates"],
           g and g["guards_between"])
        ok("the guarded site is reachable from production code",
           g and g["reach"] == REACH_PRODUCTION, g and g["reach"])

        u = by_key.get(("scripts/alpha.py", unguarded_line))
        ok("a site that subscripts the result with no guard is published unguarded",
           u and u["verdict"] == S_UNGUARDED_SUBSCRIPT and u["read_kind"] == READ_SUBSCRIPT,
           u and (u["verdict"], u["read_kind"]))
        ok("the unguarded site counts as a production risk",
           face["summary"]["production_sites_that_read_the_empty_arm_unguarded"] == 1,
           face["summary"]["production_sites_that_read_the_empty_arm_unguarded"])

        h = by_key.get(("scripts/alpha.py", handed_line))
        ok("a site that never reads the result here is published as handed on",
           h and h["read_kind"] == READ_HANDON, h and h["read_kind"])
        ok("a function nothing in the corpus calls is its own class, not a test",
           h and h["verdict"] == S_UNREACHABLE and h["reach"] == REACH_ORPHAN,
           h and (h["verdict"], h["reach"]))

        main_line = _line_of(ALPHA, 'first = guarded("x")', 0)
        m = by_key.get(("scripts/alpha.py", main_line))
        ok("an entry-point caller is production reach, and its own site is handed on",
           m and m["reach"] == REACH_PRODUCTION and m["verdict"] == S_HANDON,
           m and (m["reach"], m["verdict"]))

        t = by_key.get(("scripts/alpha.py", test_line))
        ok("a call made only from selftest is published as test-only",
           t and t["reach"] == REACH_TEST_ONLY, t and t["reach"])
        ok("a test-only site is not counted as a production risk",
           t and t["verdict"] == S_TEST_ONLY, t and t["verdict"])

        b = by_key.get(("scripts/beta.py", beta_line))
        ok("a call through another module's import alias resolves to the same callee",
           b and b["callee"] == "load", b and b["callee"])
        ok("the cross-module site is guarded by its own caller",
           b and b["verdict"] == S_GUARDED, b and b["verdict"])
        ok("reach is judged per site, not per callee",
           face["summary"]["sites_by_reach"][REACH_PRODUCTION] == 4
           and face["summary"]["sites_by_reach"][REACH_TEST_ONLY] == 1
           and face["summary"]["sites_by_reach"][REACH_ORPHAN] == 1,
           face["summary"]["sites_by_reach"])

        ok("the fixture verdict is partial, not a clean sweep",
           face["verdict"] == V_SOME, face["verdict"])
        ok("the gate passes on the built fixture", site_problems(face) == [], site_problems(face))
        ok("per-callee counts re-derive",
           face["summary"]["per_callee_site_counts"]["load"]["sites"] == 4
           and face["summary"]["per_callee_site_counts"]["guarded"]["sites"] == 2,
           face["summary"]["per_callee_site_counts"])

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["verdict"] = S_GUARDED
        ok("the gate refuses a hand-written site verdict", site_problems(doctored) != [])

        doctored2 = json.loads(json.dumps(face))
        doctored2["sites"][0]["guard_terminates_before_the_read"] = True
        doctored2["sites"][0]["guards_between"] = []
        ok("the gate refuses a covering guard with no guard row", site_problems(doctored2) != [])

        doctored3 = json.loads(json.dumps(face))
        doctored3["verdict"] = V_ALL
        ok("the gate refuses a hand-written overall verdict", site_problems(doctored3) != [])

        doctored4 = json.loads(json.dumps(face))
        doctored4["callee_census"][0]["returns_a_value"] = 0
        ok("the gate refuses a census member that does not return both kinds",
           site_problems(doctored4) != [])

        doctored5 = json.loads(json.dumps(face))
        doctored5["population_source"] = "hand-written"
        ok("the gate refuses an edited population_source", site_problems(doctored5) != [])

        empty = build(tmp, write=False, sites=[], callees={}, sources=2, failures=[])
        ok("an empty population is the explicit empty verdict",
           empty["verdict"] == V_EMPTY, empty["verdict"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks[0] - len(failures), checks[0]))
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