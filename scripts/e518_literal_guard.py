"""E518 -- is a literal return a declared empty answer or a silent default?

E514 (results/state_tilt/BUILTELSEWHERE-2026-11-08.json) found 10 literal return paths among
six genuine builders: ``return None, None, None``, ``return {}``,
``return (1.0, 1.0, [])``.  A literal return is not one thing.  ``return {}`` under
``if not paths`` is a declared empty answer -- the caller was told.  A container initialised to
empty and filled in a loop is a default that stands in for a read *if the loop never ran*, and
nothing in the signature says so.  And ``return 2`` as a sentinel is invisible next to a real
value of 2.

So the measurement is per literal arm, not per builder:

  * is a guard on the path that names the empty case?  (``if not x:``, ``if x is None:``,
    ``if len(x) == 0:``, and the ``else`` arm of a presence test)
  * or is it a mutable container initialised to empty and filled in the body?
  * and can a caller tell this arm apart from the builder's read arm from the outside --
    by a None test, by unpacking, by a truthiness/length test, by type, or not at all?

Population: every module-level function in the corpus that returns both a literal arm and a
read arm (a file, the git store, a tree scan, or an element of a loaded structure).  Nothing is
executed and nothing is rewritten.

    python scripts/e518_literal_guard.py run        # build + write the face
    python scripts/e518_literal_guard.py check      # gate the published face (fast)
    python scripts/e518_literal_guard.py verify     # re-derive from the tree and gate
    python scripts/e518_literal_guard.py selftest   # fixture arms + doctored arms
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
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e512_callee_return as e512          # noqa: E402  return paths of one function
import e514_built_elsewhere as e514        # noqa: E402  value trace (file/store/tree/series)
import e515_empty_arm_cover as e515        # noqa: E402  corpus, parse, reach via the same rules
import e507_unresolved_origin as e507      # noqa: E402  module context

CARD = "E518-IS-A-LITERAL-RETURN-A-GUARD-OR-A-SILENT-DEFAULT-IN-EVERY-BUILDER"
STUDY = "E518_literal_guard"
DATE_STAMP = "2026-11-08"
FACE_NAME = "literalguard_latest.json"
DATED_PREFIX = "LITERALGUARD"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e518_", "run_e518", "_e518", "_r1548", "LITERALGUARD", "literalguard_")

READ_KINDS = e514.READ_KINDS

# ------------------------------------------------------------------ arm classes
A_LITERAL = "the_arm_names_a_literal"
A_INITIAL = "the_arm_returns_a_container_initialised_empty_and_filled_in_the_body"
A_READ = "the_arm_hands_back_something_read_from_a_file_a_store_a_tree_or_a_panel"
A_OTHER = "the_arm_hands_back_neither_a_literal_nor_a_read"
ARM_VOCAB = (A_LITERAL, A_INITIAL, A_READ, A_OTHER)
LITERAL_FAMILY = (A_LITERAL, A_INITIAL)

# ------------------------------------------------------------------ guard classes
G_NOT_X = "an_emptiness_test_guards_the_arm"                  # ``if not x: return <lit>``
G_IS_NONE = "a_none_test_guards_the_arm"                      # ``if x is None: ...``
G_LEN_ZERO = "a_length_test_guards_the_arm"                   # ``if len(x) == 0: ...``
G_EMPTY_VALUE = "an_equality_test_against_the_empty_value_guards_the_arm"   # ``if x == '':``
G_ELSE_OF_PRESENCE = "the_arm_is_the_else_of_a_presence_test"  # ``if x: ... else: return <lit>``
G_OTHER_SUBJECT = "a_test_guards_the_arm_but_names_a_different_value"
G_NONE = "no_test_on_the_path_names_the_empty_case"
GUARD_VOCAB = (G_NOT_X, G_IS_NONE, G_LEN_ZERO, G_EMPTY_VALUE, G_ELSE_OF_PRESENCE,
               G_OTHER_SUBJECT, G_NONE)
GUARDED_VOCAB = (G_NOT_X, G_IS_NONE, G_LEN_ZERO, G_EMPTY_VALUE, G_ELSE_OF_PRESENCE)

# ------------------------------------------------------------------ shapes
SH_NONE = "none"
SH_TUPLE_OF_NONE = "a_tuple_of_none"
SH_TUPLE = "a_tuple"
SH_LIST = "a_list"
SH_DICT = "a_dict"
SH_SET = "a_set"
SH_EMPTY_TEXT = "an_empty_string"
SH_SCALAR = "a_scalar"
SH_CALL = "a_call_result"
SH_SERIES = "a_panel_or_series"
SH_NAME = "a_name"
SH_ELEMENT = "an_element_of_a_structure"
SH_EXPR = "a_computed_expression"
SHAPE_VOCAB = (SH_NONE, SH_TUPLE_OF_NONE, SH_TUPLE, SH_LIST, SH_DICT, SH_SET, SH_EMPTY_TEXT,
               SH_SCALAR, SH_CALL, SH_SERIES, SH_NAME, SH_ELEMENT, SH_EXPR)
CONTAINER_SHAPES = (SH_TUPLE, SH_LIST, SH_DICT, SH_SET, SH_TUPLE_OF_NONE)

# ------------------------------------------------------------------ distinguishability
D_IS_NONE = "a_caller_can_branch_on_is_none"
D_ARITY = "unpacking_succeeds_with_the_same_arity_so_each_element_must_be_tested_for_none"
D_TRUTHINESS = "a_caller_has_to_test_the_length_or_truthiness_of_the_result"
D_TYPE = "the_shapes_differ_so_a_caller_can_branch_on_the_type"
D_NOTHING = "nothing_short_of_reading_the_values_tells_the_two_arms_apart"
DISTINGUISH_VOCAB = (D_IS_NONE, D_ARITY, D_TRUTHINESS, D_TYPE, D_NOTHING)

# ------------------------------------------------------------------ risk of one arm
R_DECLARED = "the_arm_is_a_declared_empty_answer"
R_SILENT_INDISTINGUISHABLE = "the_arm_is_a_silent_default_a_caller_cannot_tell_apart"
R_SILENT_BUT_TESTABLE = "the_arm_is_unguarded_but_a_caller_can_test_for_it"
RISK_VOCAB = (R_DECLARED, R_SILENT_INDISTINGUISHABLE, R_SILENT_BUT_TESTABLE)

# ------------------------------------------------------------------ overall verdict
V_ALL = "every_literal_arm_of_every_builder_that_reads_is_either_guarded_or_testable"
V_SOME = "some_literal_arms_are_silent_defaults_a_caller_cannot_tell_apart"
V_ONLY_ENTRY = ("every_silent_default_belongs_to_an_entry_point_whose_sentinel_is_its_exit_code")
V_EMPTY = "no_builder_in_the_corpus_returns_both_a_literal_and_a_read"
VERDICT_VOCAB = (V_ALL, V_SOME, V_ONLY_ENTRY, V_EMPTY)

MAYBE_READ = ("read", "load", "open", "glob", "walk", "listdir", "scandir", "iterdir",
              "csv", "json", "subprocess", "parquet", "urlopen", "request")
EMPTY_CONSTANTS = (None, "", 0, False, "0")


def _now():
    return datetime.now().replace(microsecond=0).isoformat()


def _excerpt(node, limit=120):
    return e512._excerpt(node, limit)


def _src(rel, root=None):
    return e515._src(rel, root)


# ------------------------------------------------------------------ shape
def shape_of(node):
    """(kind, arity) of what a return expression hands back, from its own syntax."""
    if node is None:
        return SH_NONE, 0
    if isinstance(node, ast.Constant):
        if node.value is None:
            return SH_NONE, 0
        if isinstance(node.value, str) and not node.value:
            return SH_EMPTY_TEXT, 0
        return SH_SCALAR, 0
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        if not node.elts:
            kind = {ast.Tuple: SH_TUPLE, ast.List: SH_LIST, ast.Set: SH_SET}[type(node)]
            return kind, 0
        if isinstance(node, ast.Tuple) and all(shape_of(e)[0] == SH_NONE for e in node.elts):
            return SH_TUPLE_OF_NONE, len(node.elts)
        kind = {ast.Tuple: SH_TUPLE, ast.List: SH_LIST, ast.Set: SH_SET}[type(node)]
        return kind, len(node.elts)
    if isinstance(node, ast.Dict):
        return SH_DICT, len(node.keys)
    if isinstance(node, ast.Call):
        name = _call_name(node).lower()
        if "series" in name or "dataframe" in name or "panel" in name:
            return SH_SERIES, 0
        return SH_CALL, 0
    if isinstance(node, ast.Name):
        return SH_NAME, 0
    if isinstance(node, ast.Subscript):
        return SH_ELEMENT, 0
    if isinstance(node, ast.Attribute):
        return SH_ELEMENT, 0
    return SH_EXPR, 0


def _call_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        parts = []
        base = f
        while isinstance(base, ast.Attribute):
            parts.append(base.attr)
            base = base.value
        if isinstance(base, ast.Name):
            parts.append(base.id)
        return ".".join(reversed(parts))
    return ""


# ------------------------------------------------------------------ arm classification
def literal_only(node):
    """True when the whole expression is a literal (a bare ``return`` counts as None)."""
    if node is None:
        return True
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(literal_only(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(literal_only(k) and literal_only(v) for k, v in zip(node.keys, node.values))
    return False


READ_NAMES = tuple(e514.READ_WORDS) + tuple(e514.TREE_WORDS) + tuple(e514.EXACT_READERS) + (
    "json.load", "json.loads", "csv.dictreader", "csv.reader")


def _names_a_read(name):
    low = name.lower()
    return any(word.lower() in low for word in READ_NAMES)


def reads_something(ctx, node, params, tree, depth=0, skip=frozenset()):
    """(bool, via) -- does the expression hand back a read of a file/store/tree/panel?

    A read is followed through the function's own bindings: ``payload = json.load(fh)`` then
    ``return payload["a"]`` reads a file even though the return expression names neither.  The
    read itself is recognised by the callee's own name against e514's word lists (the same
    lists its trace uses), not by a second trace call per candidate: a census of every arm in
    the corpus cannot afford that, and the name test answers the same question.

    Answers are memoised per node for the life of one file's analysis (``_READ_CACHE`` is
    cleared in ``analyse``): without it a deeply nested arm re-walks the same sub-expression
    once per enclosing node, which made one 2,000-line module cost 15s.
    """
    if node is None or depth > 8:
        return False, ""
    key = (id(node), params, skip)
    if key in _READ_CACHE:
        return _READ_CACHE[key]
    answer = _reads_node(ctx, node, params, tree, depth, skip)
    _READ_CACHE[key] = answer
    return answer


def _reads_node(ctx, node, params, tree, depth, skip):
    if isinstance(node, ast.Call):
        name = _call_name(node)
        if _names_a_read(name):
            return True, name
        if name.split(".")[0] == "subprocess":
            return True, name
    if isinstance(node, ast.Name):
        if node.id in params:
            return False, ""
        bound = binding_at(tree, node.id, getattr(node, "lineno", 10 ** 9), skip)
        if bound is not None:
            return reads_something(ctx, bound[1], params, tree, depth + 1, skip | {bound[0]})
        return False, ""
    if isinstance(node, (ast.Subscript, ast.Attribute)):
        base = node.value
        if isinstance(base, ast.Name) and base.id in params:
            return True, "an_element_of_a_parameter"
    for child in ast.iter_child_nodes(node):
        got = reads_something(ctx, child, params, tree, depth + 1, skip)
        if got[0]:
            return got
    return False, ""


# ------------------------------------------------------------------ cached binding lookups
# e514._binding_at re-walks the whole module on every call, which turns a corpus census into
# an O(arms x tree) job.  The caches below are keyed by tree identity and never outlive one
# process run; they change no answer, only the cost.
_ASSIGN_CACHE = {}
_ASSIGN_INDEX = {}
_APPEND_CACHE = {}
_READ_CACHE = {}


def _assigns(tree):
    key = id(tree)
    got = _ASSIGN_CACHE.get(key)
    if got is None:
        got = e514._assign_nodes(tree)
        _ASSIGN_CACHE[key] = got
    return got


def _assign_index(tree):
    """name -> [(line, value)] sorted, so a lookup is not a scan of the whole module."""
    key = id(tree)
    got = _ASSIGN_INDEX.get(key)
    if got is None:
        got = {}
        for name, value, line in _assigns(tree):
            got.setdefault(name, []).append((line, value))
        for rows in got.values():
            rows.sort(key=lambda r: r[0])
        _ASSIGN_INDEX[key] = got
    return got


def binding_at(tree, name, before, skip=frozenset()):
    best = None
    for line, value in _assign_index(tree).get(name, ()):  # already sorted by line
        if line > before:
            break
        if line in skip:
            continue
        best = (line, value)
    return best


def appends_to(tree, name):
    key = (id(tree), name)
    got = _APPEND_CACHE.get(key)
    if got is None:
        got = e514._appends_to(tree, name)
        _APPEND_CACHE[key] = got
    return got


def is_empty_container(node):
    """Is this expression a container literal with nothing in it?

    ``e514._empty_container`` cannot answer this on Python 3.11: it asks
    ``not list(ast.iter_child_nodes(node))``, and every ``List``/``Dict``/``Set``/``Tuple``
    carries a ``ctx`` child node, so the guard returns False for ``[]`` and ``{}`` alike.  The
    escape hatch in ``e514.trace`` ("an empty container is a starting point, not an answer")
    therefore never fires, which is why this module answers the question itself and cross-checks
    the trace's kind on every initial-value arm.
    """
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return not node.elts
    if isinstance(node, ast.Dict):
        return not node.keys
    return False


def initial_value_arm(tree, ret, name):
    """Is ``return name`` a container initialised to empty and filled in the body?"""
    bound = binding_at(tree, name, ret.lineno)
    if bound is None:
        return None
    _line, value = bound
    if not is_empty_container(value):
        return None
    fills = appends_to(tree, name)
    if not fills:
        return None
    return {"line": value.lineno if hasattr(value, "lineno") else None,
            "initial_expression": _excerpt(value, 40), "fills": len(fills)}


# ------------------------------------------------------------------ guards
def _names_nothing_inside(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def emptiness_test_kind(test):
    """Which emptiness test this condition is, or None when it names no empty case."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return G_NOT_X
    if isinstance(test, ast.BoolOp):
        for value in test.values:
            got = emptiness_test_kind(value)
            if got:
                return got
        return None
    if isinstance(test, ast.Compare):
        lefts = [test.left] + list(test.comparators)
        for side in lefts:
            if isinstance(side, ast.Call) and isinstance(side.func, ast.Name) \
                    and side.func.id == "len":
                return G_LEN_ZERO
        # ``x is None`` is its own class: it has to be read before the equality branch, or
        # None lands in the empty-value bucket and the "is None" count reads zero
        for op, comp in zip(test.ops, test.comparators):
            if isinstance(op, ast.Is) and isinstance(comp, ast.Constant) and comp.value is None:
                return G_IS_NONE
        for comp in test.comparators:
            if isinstance(comp, ast.Constant) and comp.value in EMPTY_CONSTANTS:
                return G_EMPTY_VALUE
    return None


def presence_test(test):
    """True when the condition is a test for *having* something (its else arm names empty)."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return False
    if isinstance(test, ast.Name):
        return True
    if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == "len":
        return True
    if isinstance(test, ast.Compare):
        for op, comp in zip(test.ops, test.comparators):
            if isinstance(op, ast.IsNot):
                return True
            if isinstance(comp, ast.Constant) and comp.value not in (None, "", 0, False):
                return True
    return False


def guard_of(ret, parents, subject=frozenset()):
    """Every enclosing if-arm that names the empty case, walking up to the def.

    ``subject`` is the set of names the arm's own expression mentions.  A guard on a different
    variable is published as its own class: ``if node is None: return lits`` says something
    about ``lits`` only if ``lits`` is what was tested, and a guard that never mentions the
    returned value is not evidence that the caller was told anything.
    """
    rows = []
    node = ret
    while node in parents:
        parent = parents[node]
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            break
        if isinstance(parent, ast.If):
            entry = None
            if any(node is stmt for stmt in parent.body):
                kind = emptiness_test_kind(parent.test)
                if kind:
                    entry = {"line": parent.lineno, "test": _excerpt(parent.test),
                             "class": kind, "arm": "body",
                             "names": sorted(_names_nothing_inside(parent.test))}
            elif any(node is stmt for stmt in parent.orelse):
                if presence_test(parent.test):
                    entry = {"line": parent.lineno, "test": _excerpt(parent.test),
                             "class": G_ELSE_OF_PRESENCE, "arm": "else",
                             "names": sorted(_names_nothing_inside(parent.test))}
            if entry is not None:
                names = set(entry["names"])
                names_the_value = (not subject) or bool(names & set(subject))
                entry["names_the_returned_value"] = names_the_value
                if not names_the_value:
                    entry["test_would_have_been"] = entry["class"]
                    entry["class"] = G_OTHER_SUBJECT
                rows.append(entry)
        node = parent
    return rows


def declared_guard(chain):
    """The class of the first guard that does name this arm's own value, else G_OTHER_SUBJECT."""
    for entry in chain:
        if entry.get("names_the_returned_value") and entry.get("class") != G_OTHER_SUBJECT:
            return entry["class"]
    return G_OTHER_SUBJECT


# ------------------------------------------------------------------ distinguishability
def distinguishable(literal_shape, read_shapes):
    """Can a caller tell this literal arm from the builder's read arm, and how?"""
    kind, arity = literal_shape
    if not read_shapes:
        return D_NOTHING
    if kind == SH_NONE and all(s[0] != SH_NONE for s in read_shapes):
        return D_IS_NONE
    if kind == SH_TUPLE_OF_NONE:
        for rkind, rarty in read_shapes:
            if rkind == SH_TUPLE and rarty == arity:
                return D_ARITY
    if kind in CONTAINER_SHAPES:
        for rkind, _rarty in read_shapes:
            if rkind in CONTAINER_SHAPES or rkind in (SH_CALL, SH_SERIES, SH_SERIES, SH_ELEMENT,
                                                      SH_NAME, SH_EXPR):
                return D_TRUTHINESS
    if kind in (SH_EMPTY_TEXT, SH_SCALAR):
        for rkind, _rarty in read_shapes:
            if rkind in (SH_ELEMENT, SH_NAME, SH_SCALAR, SH_EXPR, SH_CALL, SH_EMPTY_TEXT,
                         SH_SERIES):
                return D_NOTHING
        return D_TYPE
    if all(rkind != kind for rkind, _r in read_shapes):
        return D_TYPE
    return D_NOTHING


def risk_of(guarded_by, distinguish, reach):
    if guarded_by in GUARDED_VOCAB:
        return R_DECLARED
    if distinguish in (D_NOTHING, D_ARITY):
        return R_SILENT_INDISTINGUISHABLE
    return R_SILENT_BUT_TESTABLE


# ------------------------------------------------------------------ census
def return_nodes(func):
    """[(line, Return node)] of this function's own returns (nested defs excluded)."""
    paths, _nested = e512.return_paths(func)
    wanted = {p["line"] for p in paths}
    out = []
    nested = []
    for node in ast.walk(func):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not func:
            nested.append(node)
    for node in ast.walk(func):
        if not isinstance(node, ast.Return):
            continue
        if any(e512._inside(node, sub, func) for sub in nested):
            continue
        out.append(node)
    return sorted(out, key=lambda n: (n.lineno, n.col_offset)), wanted


def arms_of(rel, func, ctx):
    """Every return arm of one function with its class and evidence."""
    params = frozenset(e512.argument_names(func))
    tree = ctx.get("tree")
    nodes, _wanted = return_nodes(func)
    arms = []
    for ret in nodes:
        expr = ret.value
        if literal_only(expr):
            kind, arity = shape_of(expr)
            arms.append({"line": ret.lineno, "class": A_LITERAL, "expr": _excerpt(expr),
                         "shape": [kind, arity], "node": ret})
            continue
        got, via = reads_something(ctx, expr, params, tree)
        if got:
            kind, arity = shape_of(expr)
            arms.append({"line": ret.lineno, "class": A_READ, "expr": _excerpt(expr),
                         "shape": [kind, arity], "via": via, "node": ret})
            continue
        if isinstance(expr, ast.Name):
            init = initial_value_arm(tree, ret, expr.id)
            if init is not None:
                kind, arity = shape_of(expr)
                # Would e514's own trace have called this arm a literal?  Its decisive branch
                # for ``return <name>`` reads: the binding is a literal, the fills are asked
                # whether any of them reads, and then the "empty container is a starting point"
                # escape hatch -- which cannot fire on this interpreter (see is_empty_container).
                # So the answer is "yes unless a fill reads", computed here without paying for
                # a trace per arm.
                fill_reads = any(reads_something(ctx, fill, params, tree)[0] for fill in
                                 appends_to(tree, expr.id))
                arms.append({"line": ret.lineno, "class": A_INITIAL, "expr": _excerpt(expr),
                             "shape": [kind, arity], "initial": init, "node": ret,
                             "e514_trace_kind": e514.K_OTHER if fill_reads else e514.K_LITERAL,
                             "fills_read_something": fill_reads})
                continue
        kind, arity = shape_of(expr)
        arms.append({"line": ret.lineno, "class": A_OTHER, "expr": _excerpt(expr),
                     "shape": [kind, arity], "node": ret})
    return arms


def analyse(root=None):
    root = root or ROOT
    # every cache below is keyed by node identity, and an identity is only unique while the
    # tree holding it is alive: clearing here is what stops a second build in the same process
    # (a selftest fixture, then the empty-population arm) inheriting the first tree's answers
    _ASSIGN_CACHE.clear()
    _ASSIGN_INDEX.clear()
    _APPEND_CACHE.clear()
    _READ_CACHE.clear()
    trees, failed = e515.parse_corpus(root)
    production_calls, test_calls = e515.call_index(trees)
    builders = []
    for rel, tree in trees:
        ctx = e507.ctx_of(root, rel)
        if ctx is None:
            continue
        ctx = dict(ctx, root=root)
        _READ_CACHE.clear()
        parents = e515.parent_map(tree)
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            arms = arms_of(rel, node, ctx)
            literals = [a for a in arms if a["class"] in LITERAL_FAMILY]
            reads = [a for a in arms if a["class"] == A_READ]
            if not literals or not reads:
                continue
            reach = e515.reach_of(node, production_calls, test_calls)
            read_shapes = [tuple(a["shape"]) for a in reads]
            rows = []
            for arm in literals:
                subject = {n.id for n in ast.walk(arm["node"].value)
                           if isinstance(n, ast.Name)} if arm["node"].value is not None else set()
                chain = guard_of(arm["node"], parents, subject)
                got = distinguishable(tuple(arm["shape"]), read_shapes)
                guarded_by = declared_guard(chain) if chain else G_NONE
                risk = risk_of(guarded_by, got, reach)
                row = {
                    "line": arm["line"],
                    "expr": arm["expr"],
                    "class": arm["class"],
                    "shape": arm["shape"],
                    "subject_names": sorted(subject),
                    "guard": chain[0] if chain else None,
                    "guarded_by": guarded_by,
                    "guards_on_the_path": chain,
                    "distinguishable_by": got,
                    "risk": risk,
                }
                if arm["class"] == A_INITIAL:
                    row["initial"] = arm["initial"]
                    row["e514_trace_calls_it_a_literal"] = (
                        arm.get("e514_trace_kind") == e514.K_LITERAL)
                    row["replaces_a_read_if_the_loop_never_ran"] = True
                rows.append(row)
            builders.append({
                "module": rel,
                "builder": node.name,
                "line": node.lineno,
                "entry_point": node.name in e515.ENTRY_FUNCS,
                "return_paths": len(arms),
                "literal_arms": len(literals),
                "read_arms": len(reads),
                "reach": reach,
                "read_shapes": [{"line": a["line"], "shape": a["shape"], "expr": a["expr"],
                                 "via": a.get("via", "")} for a in reads],
                "literal_rows": rows,
            })
    builders.sort(key=lambda b: (b["module"], b["builder"]))
    return {"builders": builders, "parse_failures": failed, "sources": len(trees)}


# ------------------------------------------------------------------ summary / verdict
def _flat(builders):
    return [row for b in builders for row in b["literal_rows"]]


def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(builders, sources):
    rows = _flat(builders)
    by_risk = _count(rows, "risk", RISK_VOCAB)
    prod = [b for b in builders if b["reach"] in (e515.REACH_PRODUCTION, e515.REACH_MODULE)]
    prod_unguarded = [r for b in prod for r in b["literal_rows"]
                      if r["guarded_by"] not in GUARDED_VOCAB]
    return {
        "sources_read": sources,
        "builders_with_a_literal_arm_and_a_read_arm": len(builders),
        "literal_arms": len(rows),
        "read_arms": sum(b["read_arms"] for b in builders),
        "literal_arms_by_class": _count(rows, "class", LITERAL_FAMILY),
        "literal_arms_by_guard": _count(rows, "guarded_by", GUARD_VOCAB),
        "literal_arms_declared_by_a_guard": len([r for r in rows
                                                 if r["guarded_by"] in GUARDED_VOCAB]),
        "literal_arms_guarded_only_by_a_test_on_another_value": len(
            [r for r in rows if r["guarded_by"] == G_OTHER_SUBJECT]),
        "literal_arms_by_distinguishability": _count(rows, "distinguishable_by",
                                                     DISTINGUISH_VOCAB),
        "literal_arms_by_risk": by_risk,
        "literal_arms_in_production_builders": len([r for b in prod for r in b["literal_rows"]]),
        "initial_value_arms": len([r for r in rows if r["class"] == A_INITIAL]),
        "initial_value_arms_the_shared_trace_calls_literals": len(
            [r for r in rows if r.get("e514_trace_calls_it_a_literal")]),
        "unguarded_literal_arms_in_production_builders": len(prod_unguarded),
        "silent_defaults_a_caller_cannot_tell_apart": by_risk.get(
            R_SILENT_INDISTINGUISHABLE, 0),
        "silent_defaults_in_entry_points": len(
            [r for b in builders if b.get("entry_point") for r in b["literal_rows"]
             if r["risk"] == R_SILENT_INDISTINGUISHABLE]),
        "silent_defaults_outside_entry_points": len(
            [r for b in builders if not b.get("entry_point") for r in b["literal_rows"]
             if r["risk"] == R_SILENT_INDISTINGUISHABLE]),
        "literal_arms_outside_entry_points": len(
            [r for b in builders if not b.get("entry_point") for r in b["literal_rows"]]),
        "builders_that_are_entry_points": len([b for b in builders if b.get("entry_point")]),
        "builders_reached_from_production_code": len(prod),
        "builders_reached_only_from_a_test": len(
            [b for b in builders if b["reach"] == e515.REACH_TEST_ONLY]),
        "builders_nothing_calls": len(
            [b for b in builders if b["reach"] == e515.REACH_ORPHAN]),
    }


def _verdict(summary):
    if summary["literal_arms"] == 0:
        return V_EMPTY
    if summary.get("silent_defaults_outside_entry_points"):
        return V_SOME
    if summary.get("silent_defaults_a_caller_cannot_tell_apart"):
        return V_ONLY_ENTRY
    return V_ALL


POPULATION_SOURCE = ("this study's own census: every module-level function under %s (plus %s) "
                     "that returns at least one literal arm and at least one arm that reads a "
                     "file, the git store, the tree or an element of a loaded structure; the "
                     "literal arm's guard is read off its own enclosing if-arms, and the read "
                     "arm's shape off its own return expression"
                     % ("/".join(e515.CORPUS_DIRS), "/".join(e515.CORPUS_ROOT_FILES)))


def build(root=None, write=True, builders=None, sources=None, failures=None):
    root = root or ROOT
    if builders is None:
        analysed = analyse(root)
        builders = analysed["builders"]
        sources = analysed["sources"]
        failures = analysed["parse_failures"]
    summary = _summary(builders, sources or 0)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("A literal return is not one thing.  For every builder in the corpus that "
                  "returns both a literal arm and a read arm, publish whether the literal sits "
                  "behind a guard that names the empty case, whether it is a container "
                  "initialised to empty and filled in the body, and whether a caller can tell "
                  "it apart from the read arm at all."),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "arm_vocab": list(ARM_VOCAB),
        "guard_vocab": list(GUARD_VOCAB),
        "shape_vocab": list(SHAPE_VOCAB),
        "distinguish_vocab": list(DISTINGUISH_VOCAB),
        "risk_vocab": list(RISK_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "builders": builders,
        "summary": summary,
        "verdict": _verdict(summary),
        "parse_failures": failures or [],
        "method_limits": [
            "static only: no arm is executed, so a guard that tests a different variable "
            "than the one read does not count as guarding this arm",
            "a guard counts only when it is an enclosing if-arm on the return's own path",
            "the read arm's concrete type is often not knowable statically; that is published "
            "as a truthiness/length test rather than claimed as a type difference",
            "a container whose fills were not resolved by the value trace is published as an "
            "initial value with its fill count, not as a read",
            "reach is a corpus fact about the builder's own name, not about the site's argument",
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
    with io.open(os.path.join(root or ROOT, "results", "state_tilt", FACE_NAME),
                 encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ gate
def face_problems(face):
    problems = []
    builders = face.get("builders") or []
    summary = face.get("summary") or {}
    rows = _flat(builders)
    if summary.get("builders_with_a_literal_arm_and_a_read_arm") != len(builders):
        problems.append("summary builder count is not the builder list length")
    if summary.get("literal_arms") != len(rows):
        problems.append("summary.literal_arms is not the literal-arm count")
    if summary.get("read_arms") != sum(b.get("read_arms") or 0 for b in builders):
        problems.append("summary.read_arms does not re-derive from the builders")
    if _count(rows, "class", LITERAL_FAMILY) != summary.get("literal_arms_by_class"):
        problems.append("literal_arms_by_class does not re-derive")
    if _count(rows, "guarded_by", GUARD_VOCAB) != summary.get("literal_arms_by_guard"):
        problems.append("literal_arms_by_guard does not re-derive")
    if summary.get("literal_arms_declared_by_a_guard") != len(
            [r for r in rows if r.get("guarded_by") in GUARDED_VOCAB]):
        problems.append("literal_arms_declared_by_a_guard does not re-derive")
    if summary.get("literal_arms_guarded_only_by_a_test_on_another_value") != len(
            [r for r in rows if r.get("guarded_by") == G_OTHER_SUBJECT]):
        problems.append("literal_arms_guarded_only_by_a_test_on_another_value does not re-derive")
    if _count(rows, "distinguishable_by", DISTINGUISH_VOCAB) != \
            summary.get("literal_arms_by_distinguishability"):
        problems.append("literal_arms_by_distinguishability does not re-derive")
    if _count(rows, "risk", RISK_VOCAB) != summary.get("literal_arms_by_risk"):
        problems.append("literal_arms_by_risk does not re-derive")
    if summary.get("silent_defaults_a_caller_cannot_tell_apart") != \
            (summary.get("literal_arms_by_risk") or {}).get(R_SILENT_INDISTINGUISHABLE):
        problems.append("silent default count is not the risk tally")
    if summary.get("initial_value_arms") != len([r for r in rows if r.get("class") == A_INITIAL]):
        problems.append("initial_value_arms does not re-derive")
    entry_silent = [r for b in builders if b.get("entry_point") for r in b["literal_rows"]
                    if r.get("risk") == R_SILENT_INDISTINGUISHABLE]
    outside_silent = [r for b in builders if not b.get("entry_point") for r in b["literal_rows"]
                      if r.get("risk") == R_SILENT_INDISTINGUISHABLE]
    if summary.get("silent_defaults_in_entry_points") != len(entry_silent):
        problems.append("silent_defaults_in_entry_points does not re-derive")
    if summary.get("silent_defaults_outside_entry_points") != len(outside_silent):
        problems.append("silent_defaults_outside_entry_points does not re-derive")
    if summary.get("silent_defaults_in_entry_points", 0) + \
            summary.get("silent_defaults_outside_entry_points", 0) != \
            summary.get("silent_defaults_a_caller_cannot_tell_apart"):
        problems.append("the entry-point split does not add up to the silent default count")
    if summary.get("builders_that_are_entry_points") != len(
            [b for b in builders if b.get("entry_point")]):
        problems.append("builders_that_are_entry_points does not re-derive")
    if summary.get("literal_arms_outside_entry_points") != len(
            [r for b in builders if not b.get("entry_point") for r in b["literal_rows"]]):
        problems.append("literal_arms_outside_entry_points does not re-derive")
    if summary.get("initial_value_arms_the_shared_trace_calls_literals") != \
            len([r for r in rows if r.get("e514_trace_calls_it_a_literal")]):
        problems.append("initial_value_arms_the_shared_trace_calls_literals does not re-derive")
    prod = [b for b in builders if b.get("reach") in (e515.REACH_PRODUCTION, e515.REACH_MODULE)]
    if summary.get("builders_reached_from_production_code") != len(prod):
        problems.append("builders_reached_from_production_code does not re-derive")
    unguarded = [r for b in prod for r in (b.get("literal_rows") or [])
                 if r.get("guarded_by") not in GUARDED_VOCAB]
    if summary.get("unguarded_literal_arms_in_production_builders") != len(unguarded):
        problems.append("unguarded_literal_arms_in_production_builders does not re-derive")
    for builder in builders:
        rows = builder.get("literal_rows") or []
        if not rows:
            problems.append("%s:%s has no literal row" % (builder.get("module"),
                                                           builder.get("builder")))
        if (builder.get("literal_arms") or 0) != len(rows):
            problems.append("%s:%s literal_arms is not its own row count"
                            % (builder.get("module"), builder.get("builder")))
        if not builder.get("read_arms"):
            problems.append("%s:%s is published with no read arm"
                            % (builder.get("module"), builder.get("builder")))
        if builder.get("reach") not in e515.REACH_VOCAB:
            problems.append("%s:%s reach outside the vocabulary"
                            % (builder.get("module"), builder.get("builder")))
        read_shapes = [tuple(s.get("shape") or ()) for s in (builder.get("read_shapes") or [])]
        for row in rows:
            if row.get("class") not in LITERAL_FAMILY:
                problems.append("%s:%s line %s is not a literal arm"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
            if row.get("guarded_by") not in GUARD_VOCAB:
                problems.append("%s:%s line %s guard outside the vocabulary"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
            if row.get("distinguishable_by") not in DISTINGUISH_VOCAB:
                problems.append("%s:%s line %s distinguish outside the vocabulary"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
            expected_dist = distinguishable(tuple(row.get("shape") or ()), read_shapes)
            if row.get("distinguishable_by") != expected_dist:
                problems.append("%s:%s line %s claims %r but its own shapes imply %r"
                                % (builder.get("module"), builder.get("builder"), row.get("line"),
                                   row.get("distinguishable_by"), expected_dist))
            expected_risk = risk_of(row.get("guarded_by"), row.get("distinguishable_by"),
                                    builder.get("reach"))
            if row.get("risk") != expected_risk:
                problems.append("%s:%s line %s risk %r is not what its guard and distinction "
                                "imply (%r)"
                                % (builder.get("module"), builder.get("builder"),
                                   row.get("line"), row.get("risk"), expected_risk))
            chain = row.get("guards_on_the_path") or []
            expected_guard = declared_guard(chain) if chain else G_NONE
            if row.get("guarded_by") != expected_guard:
                problems.append("%s:%s line %s claims guard %r but its own guard rows imply %r"
                                % (builder.get("module"), builder.get("builder"), row.get("line"),
                                   row.get("guarded_by"), expected_guard))
            if row.get("guarded_by") == G_NONE and chain:
                problems.append("%s:%s line %s says no guard but carries a guard row"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
            if row.get("guarded_by") == G_OTHER_SUBJECT and not any(
                    e.get("names_the_returned_value") is False for e in chain):
                problems.append("%s:%s line %s calls a guard unrelated to its value but no "
                                "guard row says so"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
            guard = row.get("guard")
            if row.get("guarded_by") != G_NONE and guard and guard.get("class") != row.get(
                    "guarded_by"):
                problems.append("%s:%s line %s guard row class disagrees with guarded_by"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
            if row.get("class") == A_INITIAL and not row.get("initial"):
                problems.append("%s:%s line %s is an initial value with no fill evidence"
                                % (builder.get("module"), builder.get("builder"), row.get("line")))
    if _verdict(summary) != face.get("verdict"):
        problems.append("verdict is not what the summary implies: %r" % (face.get("verdict"),))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the vocabulary")
    if (face.get("population_source") or "") != POPULATION_SOURCE:
        problems.append("population_source was edited")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = face_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    face = build(root or ROOT, write=False)
    problems = face_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s builders=%d literal_arms=%d"
          % (face["verdict"], face["summary"]["builders_with_a_literal_arm_and_a_read_arm"],
             face["summary"]["literal_arms"]))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
ALPHA = '''def guarded_literal(path):
    if not path:
        return {}
    with open(path) as fh:
        return json.load(fh)


def unguarded_none(path):
    if not os.path.exists(path):
        load = None
    with open(path) as fh:
        return json.load(fh)


def silent_none(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except OSError:
        return None


def tuple_pair(path):
    try:
        with open(path) as fh:
            data = json.load(fh)
    except OSError:
        return None, None, None
    return data["a"], data["b"], data["c"]


def sentinel(path):
    try:
        with open(path) as fh:
            return int(json.load(fh)["n"])
    except OSError:
        return 2


def filled_rows(path):
    rows = []
    try:
        with open(path) as fh:
            payload = json.load(fh)
    except OSError:
        return {}
    if payload.get("raw"):
        return payload["raw"]
    for item in payload:
        rows.append(item)
    return rows


def other_subject(node, path):
    out = []
    if node is None:
        return out
    with open(path) as fh:
        payload = json.load(fh)
    if payload.get("raw"):
        return payload
    for item in payload:
        out.append(item)
    return out


def main():
    return guarded_literal("a"), silent_none("a"), tuple_pair("a", []), sentinel("a")
'''

BETA = '''import alpha


def cross(doc):
    got = alpha.guarded_literal(doc)
    if not got:
        return []
    with open(doc) as fh:
        return [got["k"], json.load(fh)]


def main():
    return cross("x")
'''


def _line_of(text, needle, start=0):
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

    tmp = tempfile.mkdtemp(prefix="e518_")
    try:
        scripts = os.path.join(tmp, "scripts")
        os.makedirs(scripts)
        for name, text in (("alpha.py", ALPHA), ("beta.py", BETA)):
            with io.open(os.path.join(scripts, name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(text)

        face = build(tmp, write=False)
        builders = {b["builder"]: b for b in face["builders"]}
        rows = {}
        for b in face["builders"]:
            for row in b["literal_rows"]:
                rows.setdefault(b["builder"], []).append(row)

        ok("the census takes builders that return both a literal and a read",
           sorted(builders) == ["cross", "filled_rows", "guarded_literal", "other_subject",
                                "sentinel", "silent_none", "tuple_pair"],
           sorted(builders))

        g = rows["guarded_literal"][0]
        ok("a literal under `if not x` is a declared empty answer",
           g["guarded_by"] == G_NOT_X and g["risk"] == R_DECLARED, g)
        ok("the declared arm still publishes how a caller could test it",
           g["distinguishable_by"] == D_TRUTHINESS, g["distinguishable_by"])

        s = rows["silent_none"][0]
        ok("a literal None with no emptiness test is unguarded",
           s["guarded_by"] == G_NONE and s["risk"] == R_SILENT_BUT_TESTABLE, s)
        ok("a None arm is testable with `is None`",
           s["distinguishable_by"] == D_IS_NONE, s["distinguishable_by"])

        t = [r for r in rows["tuple_pair"] if r["shape"][0] == SH_TUPLE_OF_NONE][0]
        ok("a tuple of Nones against a tuple of values is the same arity",
           t["distinguishable_by"] == D_ARITY, t)
        ok("a same-arity None tuple is the silent class, not the testable one",
           t["risk"] == R_SILENT_INDISTINGUISHABLE, t["risk"])

        n = rows["sentinel"][0]
        ok("a scalar sentinel next to a read value is indistinguishable",
           n["shape"][0] == SH_SCALAR and n["distinguishable_by"] == D_NOTHING, n)
        ok("the sentinel arm is the silent class",
           n["risk"] == R_SILENT_INDISTINGUISHABLE, n["risk"])

        f = [r for r in rows["filled_rows"] if r["class"] == A_INITIAL][0]
        ok("a container initialised to empty and filled in the body is its own class",
           f["class"] == A_INITIAL and f["initial"]["fills"] >= 1, f)
        ok("the initial-value arm carries no guard",
           f["guarded_by"] == G_NONE, f["guarded_by"])
        ok("the initial-value arm is flagged as standing in for a read",
           f.get("replaces_a_read_if_the_loop_never_ran") is True, f)
        ok("the shared trace calls this initial value a literal (the escape hatch is dead)",
           f.get("e514_trace_calls_it_a_literal") is True, f.get("e514_trace_calls_it_a_literal"))
        ok("this module's own emptiness check answers what the shared helper cannot",
           is_empty_container(ast.parse("[]", mode="eval").body) is True
           and is_empty_container(ast.parse("{}", mode="eval").body) is True
           and e514._empty_container(ast.parse("[]", mode="eval").body) is False,
           (is_empty_container(ast.parse("[]", mode="eval").body),
            e514._empty_container(ast.parse("[]", mode="eval").body)))
        ok("the initial-value count is published and re-derives",
           face["summary"]["initial_value_arms"] == 3
           and face["summary"]["initial_value_arms_the_shared_trace_calls_literals"] == 3,
           (face["summary"]["initial_value_arms"],
            face["summary"]["initial_value_arms_the_shared_trace_calls_literals"]))

        o = [r for r in rows["other_subject"] if r["class"] == A_INITIAL][0]
        ok("a guard on a different variable does not declare this arm",
           o["guarded_by"] == G_OTHER_SUBJECT and o["risk"] != R_DECLARED, o)
        ok("the unrelated guard row says which value it did test",
           o["guards_on_the_path"][0].get("names_the_returned_value") is False
           and o["guards_on_the_path"][0].get("test_would_have_been") == G_IS_NONE,
           o["guards_on_the_path"][0])

        c = rows["cross"][0]
        ok("a cross-module caller with an emptiness test is declared",
           c["guarded_by"] == G_NOT_X and c["risk"] == R_DECLARED, c)

        ok("the fixture verdict is partial, not a clean sweep",
           face["verdict"] == V_SOME, face["verdict"])
        syn = [{"module": "m.py", "builder": "main", "line": 1, "entry_point": True,
                "return_paths": 2, "literal_arms": 1, "read_arms": 1,
                "reach": e515.REACH_PRODUCTION, "read_shapes": [{"line": 9,
                                                                  "shape": [SH_CALL, 0]}],
                "literal_rows": [{"class": A_LITERAL, "risk": R_SILENT_INDISTINGUISHABLE,
                                  "guarded_by": G_NONE, "guards_on_the_path": [],
                                  "distinguishable_by": D_NOTHING, "shape": [SH_SCALAR, 0]}]}]
        ok("a silent default that belongs only to an entry point is its own verdict",
           _verdict(_summary(syn, 1)) == V_ONLY_ENTRY, _verdict(_summary(syn, 1)))
        ok("the fixture's silent defaults are outside entry points",
           face["summary"]["silent_defaults_outside_entry_points"] == 4
           and face["summary"]["silent_defaults_in_entry_points"] == 0,
           face["summary"]["silent_defaults_outside_entry_points"])
        ok("the fixture gate passes on what it built",
           face_problems(face) == [], face_problems(face))
        ok("the unguarded production count re-derives",
           face["summary"]["unguarded_literal_arms_in_production_builders"] >= 3,
           face["summary"]["unguarded_literal_arms_in_production_builders"])

        doctored = json.loads(json.dumps(face))
        doctored["builders"][0]["literal_rows"][0]["risk"] = R_DECLARED
        ok("the gate refuses a hand-written risk", face_problems(doctored) != [])

        doctored2 = json.loads(json.dumps(face))
        target = None
        for b in doctored2["builders"]:
            for row in b["literal_rows"]:
                if row["guarded_by"] != G_NONE:
                    target = row
                    break
        target["guards_on_the_path"] = []
        ok("the gate refuses a claimed guard with no guard row", face_problems(doctored2) != [])

        doctored3 = json.loads(json.dumps(face))
        doctored3["verdict"] = V_ALL
        ok("the gate refuses a hand-written overall verdict", face_problems(doctored3) != [])

        doctored4 = json.loads(json.dumps(face))
        for b in doctored4["builders"]:
            b["read_shapes"] = []
            b["read_arms"] = 0
        ok("the gate refuses a builder published with no read arm", face_problems(doctored4) != [])

        doctored5 = json.loads(json.dumps(face))
        doctored5["population_source"] = "hand-written"
        ok("the gate refuses an edited population_source", face_problems(doctored5) != [])

        empty = build(tmp, write=False, builders=[], sources=2, failures=[])
        ok("an empty population is the explicit empty verdict",
           empty["verdict"] == V_EMPTY, empty["verdict"])

        # the distinction is computed from shapes, never stored as an opinion
        ok("a None literal against a None read arm is not called testable",
           distinguishable((SH_NONE, 0), [(SH_NONE, 0)]) != D_IS_NONE,
           distinguishable((SH_NONE, 0), [(SH_NONE, 0)]))
        ok("a dict literal against a panel read is a truthiness test",
           distinguishable((SH_DICT, 0), [(SH_SERIES, 0)]) == D_TRUTHINESS,
           distinguishable((SH_DICT, 0), [(SH_SERIES, 0)]))
        ok("an empty tuple literal against a 3-tuple read is a truthiness test",
           distinguishable((SH_TUPLE, 0), [(SH_TUPLE, 3)]) == D_TRUTHINESS,
           distinguishable((SH_TUPLE, 0), [(SH_TUPLE, 3)]))
        ok("`x is None` is its own guard class, not the empty-value class",
           emptiness_test_kind(ast.parse("x is None", mode="eval").body) == G_IS_NONE
           and emptiness_test_kind(ast.parse("x == ''", mode="eval").body) == G_EMPTY_VALUE
           and emptiness_test_kind(ast.parse("len(x) == 0", mode="eval").body) == G_LEN_ZERO
           and emptiness_test_kind(ast.parse("not x", mode="eval").body) == G_NOT_X
           and emptiness_test_kind(ast.parse("x > 3", mode="eval").body) is None,
           (emptiness_test_kind(ast.parse("x is None", mode="eval").body),
            emptiness_test_kind(ast.parse("x > 3", mode="eval").body)))
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