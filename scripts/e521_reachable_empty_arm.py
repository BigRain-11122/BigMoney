"""E521 -- which of the unguarded production reads sit on a REACHABLE empty arm?

E515 (results/state_tilt/EMPTYARMCOVER-2026-11-08.json) published 199 production
call sites that read a branching callee's result with no terminating guard
between the call and the read, 97 of them subscripting.  A count of unguarded
reads is not a count of crashes: the read only raises if the callee's empty arm
is actually reachable from that site, and a site that passes `[2]` to a callee
that returns nothing only when `not arg` cannot take the arm at all.

So this study takes E515's 199 rows and prices each one:

  * which empty arms the callee has at all -- E515 (and every return-path
    census before it) counts `return` statements, so a function that simply
    falls off its end has ZERO empty return paths and still returns None.  The
    implicit arm is measured here, not inherited.
  * whether the read would raise if the arm were taken (a truth test cannot
    raise on None; a subscript and a method call can).
  * whether the call site's own literal arguments exclude the arm (the guard is
    `if not x:` and the site passes a non-empty literal for x) or guarantee it
    (the same guard and the site passes None / [] / 0 / "").

Verdict per site is recomputed by the gate from the published row fields; the
summary verdict is recomputed from the rows.

Usage:
    python scripts/e521_reachable_empty_arm.py build    # write the face
    python scripts/e521_reachable_empty_arm.py check    # gate on the face
    python scripts/e521_reachable_empty_arm.py verify   # re-derive and gate in memory
    python scripts/e521_reachable_empty_arm.py selftest # fixture arms + doctored arms
"""
from __future__ import annotations

import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E521-WHICH-OF-THE-199-UNGUARDED-PRODUCTION-READS-SIT-ON-A-REACHABLE-EMPTY-ARM"
STUDY = "E521_reachable_empty_arm"
DATE_STAMP = "2026-11-08"
FACE_NAME = "emptyarmreach_latest.json"
DATED_PREFIX = "EMPTYARMREACH"
PARENT_FACE = "EMPTYARMCOVER-2026-11-08.json"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e521_", "run_e521", "_e521", "EMPTYARMREACH", "emptyarmreach_")

# --- read kinds that can raise on an empty value -----------------------------
READ_RAISES = ("subscripted", "method_call_on_the_result")
READ_BENIGN = ("truth_tested_only",)

# --- arm kinds ---------------------------------------------------------------
ARM_EXPLICIT_NONE = "an_explicit_return_that_names_nothing"
ARM_EXPLICIT_EMPTY_CONTAINER = "an_explicit_return_of_an_empty_container_literal"
ARM_IMPLICIT_FALLTHROUGH = "the_body_can_fall_off_its_own_end"
ARM_KINDS = (ARM_EXPLICIT_NONE, ARM_EXPLICIT_EMPTY_CONTAINER, ARM_IMPLICIT_FALLTHROUGH)

# --- arm reachability from the call site -------------------------------------
REACH_UNCONDITIONAL = "the_arm_sits_outside_every_branch_of_the_callee"
REACH_EXCLUDED_BY_LITERAL = "the_call_site_passes_a_literal_that_the_arm_s_guard_rejects"
REACH_GUARANTEED_BY_LITERAL = "the_call_site_passes_a_literal_that_the_arm_s_guard_accepts"
REACH_UNDECIDED_NON_LITERAL = "the_arm_s_guard_names_a_parameter_but_the_site_passes_no_literal"
REACH_UNDECIDED_OTHER_GUARD = "the_arm_is_behind_a_test_that_does_not_name_the_callee_s_parameters"
REACHABILITIES = (
    REACH_UNCONDITIONAL,
    REACH_EXCLUDED_BY_LITERAL,
    REACH_GUARANTEED_BY_LITERAL,
    REACH_UNDECIDED_NON_LITERAL,
    REACH_UNDECIDED_OTHER_GUARD,
)
REACH_REACHES = (REACH_UNCONDITIONAL, REACH_GUARANTEED_BY_LITERAL)

# --- site verdicts -----------------------------------------------------------
V_RAISES_AND_ARM_REACHES = "the_read_would_raise_and_no_empty_arm_is_excluded_by_the_call_s_own_arguments"
V_RAISES_ALL_ARMS_EXCLUDED = "the_read_would_raise_but_every_empty_arm_is_excluded_by_the_call_s_own_literal_arguments"
V_RAISES_NO_EMPTY_ARM = "the_read_would_raise_on_nothing_but_the_callee_has_no_empty_arm_on_any_path"
V_RAISES_UNDECIDED = "the_read_would_raise_and_the_arm_s_reachability_is_not_decidable_from_the_call_site"
V_BENIGN_TRUTH_TEST = "the_read_is_a_truth_test_so_an_empty_value_does_not_raise"
V_TERNARY_GUARDED = "the_read_sits_inside_a_conditional_expression_that_tests_the_same_name_a_guard_the_parent_cannot_see"
SITE_VERDICTS = (
    V_TERNARY_GUARDED,
    V_RAISES_AND_ARM_REACHES,
    V_RAISES_ALL_ARMS_EXCLUDED,
    V_RAISES_NO_EMPTY_ARM,
    V_RAISES_UNDECIDED,
    V_BENIGN_TRUTH_TEST,
)

# --- the guard the parent cannot see -----------------------------------------
GUARD_TERNARY = "a_conditional_expression_on_the_read_line_tests_the_read_s_own_root_name"
GUARD_NONE_VISIBLE = "no_guard_is_visible_on_the_read_line"
READ_GUARDS = (GUARD_TERNARY, GUARD_NONE_VISIBLE)


def _now():
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def load_parent(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", PARENT_FACE), encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """E515's unguarded production reads, in the parent's own vocabulary."""
    out = []
    for row in parent["sites"]:
        if row["reach"] != "inside_a_function_production_code_calls":
            continue
        if row["verdict"] not in (
            "the_result_is_subscripted_with_no_guard_between",
            "the_result_is_read_in_production_with_no_guard_between",
        ):
            continue
        out.append(row)
    return out


# --- parsing helpers ---------------------------------------------------------
_FILE_CACHE = {}


def parse_file(root, rel):
    key = rel
    if key in _FILE_CACHE:
        return _FILE_CACHE[key]
    path = os.path.join(root, rel)
    tree = None
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        tree = ast.parse(raw.decode("utf-8", "replace"))
    except Exception:
        tree = None
    _FILE_CACHE[key] = tree
    return tree


def find_function(tree, name, lineno):
    """The function the parent pinned by line; falls back to name-only."""
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            hits.append(node)
    for node in hits:
        if node.lineno == lineno:
            return node
    return hits[0] if len(hits) == 1 else (hits[0] if hits else None)


def inner_body(nodes):
    """Walk a statement list but do not descend into nested defs/classes."""
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield node


def walk_own(node, parents, stack=()):
    """Yield (node, control_stack) inside one function body, never nested defs."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        control = stack
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            control = stack + (child,)
        yield child, control
        yield from walk_own(child, parents, control)


CONTAINER_LITERALS = (ast.List, ast.Tuple, ast.Set, ast.Dict)


def return_kind(node):
    if not isinstance(node, ast.Return):
        return None
    if node.value is None:
        return ARM_EXPLICIT_NONE
    if isinstance(node.value, ast.Constant) and node.value.value is None:
        return ARM_EXPLICIT_NONE
    if isinstance(node.value, CONTAINER_LITERALS) and not getattr(node.value, "elts", None) and not getattr(node.value, "keys", None):
        return ARM_EXPLICIT_EMPTY_CONTAINER
    if isinstance(node.value, ast.Call) and not node.value.args and not node.value.keywords:
        fname = getattr(node.value.func, "id", None) or getattr(node.value.func, "attr", None)
        if fname in ("dict", "list", "set", "tuple"):
            return ARM_EXPLICIT_EMPTY_CONTAINER
    return None


def always_terminates(stmts):
    """Conservative: does this statement list end on every path in return/raise?"""
    for node in reversed(stmts):
        if isinstance(node, ast.Return):
            return True
        if isinstance(node, ast.Raise):
            return True
        if isinstance(node, ast.If):
            if not node.orelse:
                return False
            return always_terminates(node.body) and always_terminates(node.orelse)
        if isinstance(node, ast.Try):
            parts = [always_terminates(node.body)]
            parts += [always_terminates(h.body) for h in node.handlers]
            if node.orelse:
                parts.append(always_terminates(node.orelse))
            return all(parts)
        if isinstance(node, ast.With):
            return always_terminates(node.body)
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                return True
            return False
        if isinstance(node, (ast.For, ast.AsyncFor)):
            return False
        return False
    return False


# --- literal argument classification -----------------------------------------
FALSY_CONST = (None, False, 0, 0.0, "")


def literal_class(node):
    """truthy_literal / falsy_literal / not_a_literal."""
    if isinstance(node, ast.Constant):
        return "falsy_literal" if node.value in FALSY_CONST else "truthy_literal"
    if isinstance(node, CONTAINER_LITERALS):
        if isinstance(node, ast.Dict):
            return "truthy_literal" if node.keys else "falsy_literal"
        return "truthy_literal" if node.elts else "falsy_literal"
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return "not_a_literal"
    return "not_a_literal"


def call_arguments(call_expr):
    """positional literal classes from the site's own call text."""
    try:
        call = ast.parse(call_expr, mode="eval").body
    except Exception:
        return None, {}
    if not isinstance(call, ast.Call):
        return None, {}
    pos = [literal_class(a) for a in call.args]
    kw = {k.arg: literal_class(k.value) for k in call.keywords if k.arg}
    if any(isinstance(a, ast.Starred) for a in call.args):
        pos = pos + ["not_a_literal"]
    return pos, kw


def parameter_names(fn):
    args = fn.args
    names = [a.arg for a in list(getattr(args, "posonlyargs", [])) + list(args.args)]
    return names, [a.arg for a in args.kwonlyargs]


def _is_emptiness_test(test, name):
    """Is this an `if not X:` / `if X is None:` style emptiness test on name?"""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return isinstance(test.operand, ast.Name) and test.operand.id == name
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        left, op, right = test.left, test.ops[0], test.comparators[0]
        for a, b in ((left, right), (right, left)):
            if isinstance(a, ast.Name) and a.id == name:
                if isinstance(op, ast.Is) and isinstance(b, ast.Constant) and b.value is None:
                    return True
                if isinstance(b, (ast.List, ast.Tuple, ast.Dict, ast.Set)) and not (b.elts if not isinstance(b, ast.Dict) else b.keys):
                    return True
                if isinstance(b, ast.Call) and getattr(b.func, "id", None) == "len" and not b.args:
                    return False
    return False


def _names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def arm_reachability(arm_kind, control_stack, test_of, posargs, kwargs, names, kwonly):
    """Where does this arm sit relative to the call site's own literals?"""
    if arm_kind == ARM_IMPLICIT_FALLTHROUGH:
        return REACH_UNCONDITIONAL
    ifs = [c for c in control_stack if isinstance(c, ast.If)]
    if not ifs:
        return REACH_UNCONDITIONAL
    for node in ifs:
        test = test_of.get(id(node))
        if test is None:
            continue
        hits = _names_in(test) & set(names + kwonly)
        if not hits:
            return REACH_UNDECIDED_OTHER_GUARD
        name = sorted(hits)[0]
        if name in kwargs:
            klass = kwargs[name]
        else:
            idx = names.index(name) if name in names else None
            klass = posargs[idx] if idx is not None and idx < len(posargs) else "not_a_literal"
        if not _is_emptiness_test(test, name):
            return REACH_UNDECIDED_OTHER_GUARD
        if klass == "truthy_literal":
            return REACH_EXCLUDED_BY_LITERAL
        if klass == "falsy_literal":
            return REACH_GUARANTEED_BY_LITERAL
        return REACH_UNDECIDED_NON_LITERAL
    return REACH_UNDECIDED_OTHER_GUARD


def callee_arms(root, rel, name, lineno, call_expr):
    """Every empty arm of the callee, with its reachability from this site."""
    tree = parse_file(root, rel)
    if tree is None:
        return None, "callee_source_does_not_parse"
    fn = find_function(tree, name, lineno)
    if fn is None:
        return None, "callee_not_found_in_its_own_source"

    names, kwonly = parameter_names(fn)
    posargs, kwargs = call_arguments(call_expr)
    posargs = posargs or []
    kwargs = kwargs or {}

    test_of = {}
    for node, _stack in walk_own(fn, None):
        if isinstance(node, ast.If):
            test_of[id(node)] = node.test
    # walk_own yields children of fn, so the If nodes themselves are yielded;
    # rebuild the map from the yielded set to be safe.
    for node in ast.walk(fn):
        if isinstance(node, ast.If):
            test_of[id(node)] = node.test

    arms = []
    for node, stack in walk_own(fn, None):
        kind = return_kind(node)
        if kind:
            arms.append(
                {
                    "kind": kind,
                    "line": node.lineno,
                    "reach": arm_reachability(kind, stack, test_of, posargs, kwargs, names, kwonly),
                }
            )
    if not always_terminates(fn.body):
        arms.append({"kind": ARM_IMPLICIT_FALLTHROUGH, "line": fn.lineno, "reach": REACH_UNCONDITIONAL})
    return arms, None


def root_name(expr_text):
    """The name the read hangs off: `d.get` -> d, `sig['delta']` -> sig."""
    try:
        node = ast.parse(expr_text, mode="eval").body
    except Exception:
        return None
    while True:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
            continue
        if isinstance(node, ast.Call):
            node = node.func
            continue
        if isinstance(node, ast.Compare):  # a truth test written as a comparison
            node = node.left
            continue
        return None


def read_line_guard(root, rel, line, read_expr):
    """A conditional expression that tests the read's own root name is a guard.

    E515 looks for statements between the call and the read; `x.get('k') if
    isinstance(x, dict) else None` puts the guard INSIDE the read line, so that
    arm reads as unguarded.  Measured here, not assumed.
    """
    tree = parse_file(root, rel)
    if tree is None or not line or not read_expr:
        return GUARD_NONE_VISIBLE
    name = root_name(read_expr)
    if not name:
        return GUARD_NONE_VISIBLE
    for node in ast.walk(tree):
        if not isinstance(node, ast.IfExp):
            continue
        if not (node.lineno <= line <= getattr(node, "end_lineno", node.lineno)):
            continue
        if name in _names_in(node.test):
            return GUARD_TERNARY
    return GUARD_NONE_VISIBLE


def site_verdict(read_kind, arms, error, guard=GUARD_NONE_VISIBLE):
    if guard == GUARD_TERNARY:
        return V_TERNARY_GUARDED
    if error:
        return V_RAISES_UNDECIDED
    if read_kind in READ_BENIGN:
        return V_BENIGN_TRUTH_TEST
    if not arms:
        return V_RAISES_NO_EMPTY_ARM
    reaches = [a for a in arms if a["reach"] in REACH_REACHES]
    if reaches:
        return V_RAISES_AND_ARM_REACHES
    excluded = [a for a in arms if a["reach"] == REACH_EXCLUDED_BY_LITERAL]
    if len(excluded) == len(arms):
        return V_RAISES_ALL_ARMS_EXCLUDED
    return V_RAISES_UNDECIDED


def analyse(root=None):
    root = root or ROOT
    parent = load_parent(root)
    rows = []
    errors = {}
    for site in population(parent):
        arms, error = callee_arms(
            root, site["callee_rel"], site["callee"], site["callee_line"], site["call_expression"]
        )
        arms = arms or []
        guard = read_line_guard(root, site["source"], site["first_read_line"], site["first_read_expression"])
        verdict = site_verdict(site["read_kind"], arms, error, guard)
        if error:
            errors[error] = errors.get(error, 0) + 1
        rows.append(
            {
                "source": site["source"],
                "line": site["line"],
                "callee": site["callee"],
                "callee_rel": site["callee_rel"],
                "callee_line": site["callee_line"],
                "call_expression": site["call_expression"],
                "first_read_expression": site["first_read_expression"],
                "first_read_line": site["first_read_line"],
                "read_kind": site["read_kind"],
                "read_guard": guard,
                "arm_kinds": sorted({a["kind"] for a in arms}),
                "arm_reaches": sorted({a["reach"] for a in arms}),
                "empty_arms": len(arms),
                "verdict": verdict,
                "error": error,
            }
        )
    return rows, parent, errors


def summary(rows, parent):
    by_verdict = {v: 0 for v in SITE_VERDICTS}
    for r in rows:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
    by_read = {}
    for r in rows:
        by_read.setdefault(r["read_kind"], {}).setdefault(r["verdict"], 0)
        by_read[r["read_kind"]][r["verdict"]] += 1
    implicit_only = [r for r in rows if r["arm_kinds"] == [ARM_IMPLICIT_FALLTHROUGH]]
    no_arm = [r for r in rows if r["empty_arms"] == 0]
    reaches = [r for r in rows if r["verdict"] == V_RAISES_AND_ARM_REACHES]
    ternary = [r for r in rows if r["read_guard"] == GUARD_TERNARY]
    return {
        "population": len(rows),
        "parent_population": len(population(parent)),
        "parent_verdict": parent["verdict"],
        "by_verdict": by_verdict,
        "by_read_kind": by_read,
        "by_read_guard": {
            g: sum(1 for r in rows if r["read_guard"] == g) for g in READ_GUARDS
        },
        "sites_whose_only_empty_arm_is_the_implicit_fallthrough": len(implicit_only),
        "sites_that_carry_an_implicit_fallthrough_arm_the_return_path_census_cannot_count": sum(
            1 for r in rows if ARM_IMPLICIT_FALLTHROUGH in r["arm_kinds"]
        ),
        "rows_with_no_empty_arm_located_here": len(no_arm),
        "sites_where_a_raising_read_takes_a_reachable_empty_arm": len(reaches),
        "sites_the_parent_called_unguarded_that_a_conditional_expression_already_guards": len(ternary),
        "ternary_guarded_sites_that_would_have_raised": sum(
            1 for r in ternary if r["arm_reaches"] and set(r["arm_reaches"]) & set(REACH_REACHES)
        ),
        "raising_sites": by_verdict[V_RAISES_AND_ARM_REACHES]
        + by_verdict[V_RAISES_ALL_ARMS_EXCLUDED]
        + by_verdict[V_RAISES_NO_EMPTY_ARM]
        + by_verdict[V_RAISES_UNDECIDED],
        "benign_truth_tests": by_verdict[V_BENIGN_TRUTH_TEST],
        "distinct_callees": len({(r["callee_rel"], r["callee_line"]) for r in rows}),
        "distinct_sources": len({r["source"] for r in rows}),
    }


def verdict_of(summary):
    if summary["sites_where_a_raising_read_takes_a_reachable_empty_arm"]:
        return "some_unguarded_production_read_reaches_an_empty_arm_with_nothing_between_it_and_the_crash"
    if summary["by_verdict"][V_RAISES_UNDECIDED]:
        return "no_arm_is_unconditionally_reachable_but_some_arm_s_reachability_is_not_decidable_from_the_call_site"
    if summary["raising_sites"] == 0:
        return "every_unguarded_production_read_is_a_truth_test_so_a_count_of_unguarded_reads_overstates_the_crash_surface"
    return "every_raising_read_s_own_literal_arguments_exclude_every_empty_arm"


def build(root=None, write=True):
    root = root or ROOT
    rows, parent, errors = analyse(root)
    summ = summary(rows, parent)
    face = {
        "card": CARD,
        "study": STUDY,
        "title": (
            "A count of unguarded reads is not a count of crashes: for each of E515's 199 unguarded "
            "production reads, enumerate every empty arm of the callee -- including the implicit one a "
            "return-path census cannot see -- and ask whether that arm is reachable from this call site's "
            "own literal arguments"
        ),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": (
            "E515's published face results/state_tilt/EMPTYARMCOVER-2026-11-08.json, rows with "
            "reach=inside_a_function_production_code_calls and verdict in "
            "(the_result_is_subscripted_with_no_guard_between, the_result_is_read_in_production_with_no_guard_between); "
            "arm reachability measured here by re-parsing the callee's own source at the pinned (rel, line)"
        ),
        "arm_kind_vocab": list(ARM_KINDS),
        "reachability_vocab": list(REACHABILITIES),
        "read_guard_vocab": list(READ_GUARDS),
        "verdict_vocab": list(SITE_VERDICTS),
        "summary": summ,
        "verdict": verdict_of(summ),
        "callee_lookup_errors": errors,
        "method_limits": [
            "reachability is decided only for the shape `if not x:` / `if x is None:` on a parameter; any other test is published as undecided rather than guessed",
            "a literal argument excludes an arm only when the guard is the emptiness test on that very parameter; a truthy literal passed to `if x > 0:` proves nothing and is not counted",
            "the implicit fallthrough arm is detected with a conservative always-terminates walk (Return/Raise, if/else, try with all handlers); a loop-only body is treated as falling through",
            "the read would raise is inferred from the read kind the parent published (subscript / method call), not from re-reading the site",
            "the conditional-expression guard is line-scoped: an IfExp that spans the read line and names the read's root counts as a guard, even where it guards a sibling expression on the same line",
        ],
        "sites": rows,
    }
    if write:
        d = os.path.join(root, "results", "state_tilt")
        dated = os.path.join(d, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
        with open(dated, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(os.path.join(d, FACE_NAME), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return face


def load_face(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", FACE_NAME), encoding="utf-8") as fh:
        return json.load(fh)


def site_problems(face):
    """Every published row must re-derive from its own fields."""
    problems = []
    seen = set()
    recomputed_by_verdict = {v: 0 for v in SITE_VERDICTS}
    for row in face["sites"]:
        key = (row["source"], row["line"], row["callee"])
        if key in seen:
            problems.append("duplicate row %s" % (key,))
        seen.add(key)
        if row["read_guard"] not in READ_GUARDS:
            problems.append("row %s:%s carries an unknown read_guard" % (row["source"], row["line"]))
        if row["read_guard"] == GUARD_TERNARY:
            want = V_TERNARY_GUARDED
        elif row["read_kind"] in READ_BENIGN:
            want = V_BENIGN_TRUTH_TEST
        elif row["empty_arms"] == 0:
            want = V_RAISES_NO_EMPTY_ARM
        elif set(row["arm_reaches"]) & set(REACH_REACHES):
            want = V_RAISES_AND_ARM_REACHES
        elif set(row["arm_reaches"]) <= {REACH_EXCLUDED_BY_LITERAL}:
            want = V_RAISES_ALL_ARMS_EXCLUDED
        else:
            want = V_RAISES_UNDECIDED
        if row["verdict"] != want:
            problems.append("row %s:%s verdict %r does not re-derive (%r)" % (row["source"], row["line"], row["verdict"], want))
        if row["empty_arms"] and not row["arm_kinds"]:
            problems.append("row %s:%s has arms with no kinds" % (row["source"], row["line"]))
        recomputed_by_verdict[want] = recomputed_by_verdict.get(want, 0) + 1
    if recomputed_by_verdict != face["summary"]["by_verdict"]:
        problems.append("summary.by_verdict does not re-derive from the rows")
    if face["summary"]["population"] != len(face["sites"]):
        problems.append("summary.population does not equal the row count")
    if len(face["sites"]) != face["summary"]["parent_population"]:
        problems.append("population is not the parent's unguarded production read set")
    raises = sum(1 for r in face["sites"] if r["read_kind"] in READ_RAISES and r["read_guard"] != GUARD_TERNARY)
    if face["summary"]["raising_sites"] != raises:
        problems.append("summary.raising_sites does not re-derive")
    if face["summary"]["benign_truth_tests"] != sum(1 for r in face["sites"] if r["verdict"] == V_BENIGN_TRUTH_TEST):
        problems.append("benign count does not re-derive")
    ternary = sum(1 for r in face["sites"] if r["read_guard"] == GUARD_TERNARY)
    if face["summary"]["sites_the_parent_called_unguarded_that_a_conditional_expression_already_guards"] != ternary:
        problems.append("ternary guard count does not re-derive")
    if face["verdict"] != verdict_of(face["summary"]):
        problems.append("verdict does not re-derive from the summary")
    reachable = sum(1 for r in face["sites"] if r["verdict"] == V_RAISES_AND_ARM_REACHES)
    if face["summary"]["sites_where_a_raising_read_takes_a_reachable_empty_arm"] != reachable:
        problems.append("sites_where_a_raising_read_takes_a_reachable_empty_arm does not re-derive")
    armless = sum(1 for r in face["sites"] if r["empty_arms"] == 0)
    if face["summary"]["rows_with_no_empty_arm_located_here"] != armless:
        problems.append("rows_with_no_empty_arm_located_here does not re-derive")
    if face["summary"]["distinct_callees"] != len({(r["callee_rel"], r["callee_line"]) for r in face["sites"]}):
        problems.append("distinct_callees does not re-derive")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = site_problems(face)
    return problems


def verify(root=None):
    root = root or ROOT
    on_disk = load_face(root)
    rebuilt = build(root, write=False)
    problems = check(on_disk, root)
    for key in ("verdict", "summary", "sites"):
        if json.dumps(on_disk[key], sort_keys=True, ensure_ascii=False) != json.dumps(
            rebuilt[key], sort_keys=True, ensure_ascii=False
        ):
            problems.append("rebuilt %s differs from the published face" % key)
    return problems


# --- selftest ----------------------------------------------------------------
FIXTURE = '''
def unconditional_none(x):
    if x:
        return 1
    return None

def falls_off(vals):
    if vals:
        return vals[0]

def emptiness_guard(x):
    if not x:
        return None
    return x[0]

def other_guard(n):
    if n > 3:
        return None
    return n

def safe(x):
    if not x:
        raise ValueError(x)
    return x
'''


def selftest():
    import tempfile

    fails = []
    ran = []

    def eq(name, got, want):
        ran.append(name)
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

    tmp = tempfile.mkdtemp()
    try:
        rel = "fixture_mod.py"
        with open(os.path.join(tmp, rel), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)

        def arms_for(fn, call):
            tree = parse_file(tmp, rel)
            hits = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == fn]
            arms, err = callee_arms(tmp, rel, fn, hits[0].lineno, call)
            return arms, err

        arms, err = arms_for("unconditional_none", "unconditional_none(1)")
        eq("unconditional kinds", sorted({a["kind"] for a in arms}), sorted({ARM_EXPLICIT_NONE}))
        eq("unconditional reach", sorted({a["reach"] for a in arms}), [REACH_UNCONDITIONAL])
        eq("unconditional verdict", site_verdict("subscripted", arms, err), V_RAISES_AND_ARM_REACHES)

        arms, err = arms_for("falls_off", "falls_off([1])")
        eq("fallthrough kinds", sorted({a["kind"] for a in arms}), [ARM_IMPLICIT_FALLTHROUGH])
        eq("fallthrough verdict", site_verdict("subscripted", arms, err), V_RAISES_AND_ARM_REACHES)
        # the return-path census sees nothing here: this is the arm E515 cannot count
        eq("fallthrough is not an explicit return", [a["kind"] for a in arms if a["kind"] != ARM_IMPLICIT_FALLTHROUGH], [])

        arms, err = arms_for("emptiness_guard", "emptiness_guard([1, 2])")
        eq("literal excludes the arm", arms[0]["reach"], REACH_EXCLUDED_BY_LITERAL)
        eq("excluded verdict", site_verdict("subscripted", arms, err), V_RAISES_ALL_ARMS_EXCLUDED)

        arms, err = arms_for("emptiness_guard", "emptiness_guard(None)")
        eq("literal guarantees the arm", arms[0]["reach"], REACH_GUARANTEED_BY_LITERAL)
        eq("guaranteed verdict", site_verdict("subscripted", arms, err), V_RAISES_AND_ARM_REACHES)

        arms, err = arms_for("emptiness_guard", "emptiness_guard(vals)")
        eq("non-literal is undecided", arms[0]["reach"], REACH_UNDECIDED_NON_LITERAL)
        eq("undecided verdict", site_verdict("subscripted", arms, err), V_RAISES_UNDECIDED)

        arms, err = arms_for("other_guard", "other_guard([1])")
        eq("a non-emptiness test proves nothing", arms[0]["reach"], REACH_UNDECIDED_OTHER_GUARD)

        arms, err = arms_for("other_guard", "other_guard([1])")
        eq("undecided-other verdict", site_verdict("subscripted", arms, err), V_RAISES_UNDECIDED)

        arms, err = arms_for("safe", "safe([1])")
        eq("no empty arm", arms, [])

        # a conditional expression on the read line is a guard the parent cannot see
        eq("root name of an attribute read", root_name("d.get"), "d")
        eq("root name of a subscript read", root_name("sig['delta']"), "sig")
        tree = parse_file(tmp, rel)
        with open(os.path.join(tmp, "ternary_mod.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(
                "def f(p):\n"
                "    d = 1\n"
                "    return d.get('k') if d else None\n"
                "def g(p):\n"
                "    d = 1\n"
                "    return d.get('k')\n"
            )
        eq(
            "an IfExp that tests the read's own name is a guard",
            read_line_guard(tmp, "ternary_mod.py", 3, "d.get"),
            GUARD_TERNARY,
        )
        eq(
            "a bare read line has no visible guard",
            read_line_guard(tmp, "ternary_mod.py", 6, "d.get"),
            GUARD_NONE_VISIBLE,
        )
        eq(
            "a ternary guard outranks the arm arms",
            site_verdict("subscripted", [{"kind": ARM_EXPLICIT_NONE, "line": 1, "reach": REACH_UNCONDITIONAL}], None, GUARD_TERNARY),
            V_TERNARY_GUARDED,
        )

        # doctored arms: a row whose verdict contradicts its own fields must fail the gate
        good = {
            "card": CARD,
            "verdict": "every_raising_read_s_own_literal_arguments_exclude_every_empty_arm",
            "summary": {
                "population": 1,
                "parent_population": 1,
                "by_verdict": {v: 0 for v in SITE_VERDICTS},
                "raising_sites": 1,
                "benign_truth_tests": 0,
                "sites_where_a_raising_read_takes_a_reachable_empty_arm": 0,
                "sites_the_parent_called_unguarded_that_a_conditional_expression_already_guards": 0,
                "distinct_callees": 1,
            },
            "sites": [
                {
                    "source": "a.py",
                    "line": 1,
                    "callee": "f",
                    "callee_rel": "a.py",
                    "callee_line": 1,
                    "read_kind": "subscripted",
                    "read_guard": GUARD_NONE_VISIBLE,
                    "arm_kinds": [ARM_EXPLICIT_NONE],
                    "arm_reaches": [REACH_EXCLUDED_BY_LITERAL],
                    "empty_arms": 1,
                    "verdict": V_RAISES_ALL_ARMS_EXCLUDED,
                }
            ],
        }
        good["summary"]["by_verdict"][V_RAISES_ALL_ARMS_EXCLUDED] = 1
        eq("clean fixture passes", site_problems(good), [])

        doctored = json.loads(json.dumps(good))
        doctored["sites"][0]["verdict"] = V_RAISES_AND_ARM_REACHES
        eq(
            "a verdict that contradicts its own fields is refused",
            any("does not re-derive" in p for p in site_problems(doctored)),
            True,
        )

        doctored = json.loads(json.dumps(good))
        doctored["summary"]["raising_sites"] = 0
        eq(
            "a summary that contradicts the rows is refused",
            any("raising_sites" in p for p in site_problems(doctored)),
            True,
        )

        doctored = json.loads(json.dumps(good))
        doctored["sites"][0]["empty_arms"] = 0
        doctored["sites"][0]["arm_kinds"] = []
        eq(
            "an armless row cannot keep an arm reachability",
            any("does not re-derive" in p for p in site_problems(doctored)),
            True,
        )

        doctored = json.loads(json.dumps(good))
        doctored["summary"]["population"] = 2
        eq(
            "population must equal the row count",
            any("population" in p for p in site_problems(doctored)),
            True,
        )
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print("[FAIL] " + f)
    print("%d/%d" % (len(ran) - len(fails), len(ran)))
    if fails:
        return 1
    print("selftest clean")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "build":
        face = build()
        print(json.dumps({"face": FACE_NAME, "population": len(face["sites"]), "verdict": face["verdict"]}))
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        problems = check()
        for p in problems:
            print("[FAIL] " + p)
        print("problems=%d" % len(problems))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("[FAIL] " + p)
        print("problems=%d" % len(problems))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())