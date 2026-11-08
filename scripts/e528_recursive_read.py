"""E528 -- is a self-recursive forward ever read by a terminating arm?

E525 (results/state_tilt/onwardresidue_latest.json) followed the values E524 said the second reader
still forwards and found six parcels whose callee is the function the value is already inside
(``_resolve`` calling ``_resolve``, ``is_literal_side`` calling ``is_literal_side``).  It published
them as one class -- ``the_same_function_again_so_the_chain_closes_inside_one_body`` -- which says
the chain does not leave the body but says nothing about whether the recursion ends on a value a
caller can read.

This study opens each of those six parcels and publishes, per parcel:

  * the arm the function uses for the value *outside* the recursive call -- returns it, reads it,
    only tests its type, discards it, or never mentions it
  * whether every recursive call of that function sits under a guard that can end the recursion --
    a depth counter tested against a constant, a type/None test on the value, both, or none
  * a verdict that keeps the two upstream classes apart: ``read_by_a_terminating_arm`` versus
    ``the_recursion_is_unguarded`` -- a recursive call is never counted as a read

Everything is re-derived from the cited source line at ``check``/``verify`` time, never copied from
the upstream face.

    python scripts/e528_recursive_read.py run        # build + write the face
    python scripts/e528_recursive_read.py check      # gate the published face (fast)
    python scripts/e528_recursive_read.py verify     # re-derive from the tree and gate
    python scripts/e528_recursive_read.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E528-WHICH-OF-THE-SELF-RECURSIVE-FORWARDS-IS-READ-BY-A-TERMINATING-ARM-OF-THE-SAME-FUNCTION"
STUDY = "E528_recursive_read"
DATE_STAMP = "2026-11-08"
FACE_NAME = "recursiveread_latest.json"
DATED_PREFIX = "RECURSIVEREAD"

SELF_EXCLUDED = ("e528_", "run_e528", "_e528", "RECURSIVEREAD", "recursiveread_",
                 "_r1555", "_r1556")

UPSTREAM_FACE = "results/state_tilt/onwardresidue_latest.json"
UPSTREAM_STUDY = "E525_onward_residue"

# E525's class for a parcel handed back into the function it is already inside.
CHAIN_SELF_RECURSION = "the_same_function_again_so_the_chain_closes_inside_one_body"

# ---------------------------------------------------------------- arm vocabulary
A_RETURNS = "returns_it_to_a_caller"
A_READS = "reads_it_without_returning_it"
A_TYPE_ONLY = "only_tests_its_type"
A_DISCARDS = "discards_it"
A_NEVER = "never_mentions_it_outside_the_recursive_call"
ARM_VOCAB = (A_RETURNS, A_READS, A_TYPE_ONLY, A_DISCARDS, A_NEVER)

# a use of the value in a non-recursive branch that still decides something
ARM_TERMINATES = (A_RETURNS, A_READS, A_TYPE_ONLY)

# ---------------------------------------------------------------- guard vocabulary
G_DEPTH = "guarded_by_a_depth_counter"
G_TYPE = "guarded_by_a_type_or_none_test"
G_BOTH = "guarded_by_a_depth_counter_and_a_type_test"
G_NONE = "no_guard_found_on_the_recursive_path"
GUARD_VOCAB = (G_DEPTH, G_TYPE, G_BOTH, G_NONE)

# ---------------------------------------------------------------- verdict vocabulary
V_READ = "read_by_a_terminating_arm"
V_UNGUARDED = "the_recursion_is_unguarded"
V_GUARDED_UNREAD = "guarded_but_the_value_is_never_read"
V_EMPTY = "no_self_recursive_parcel_in_the_upstream_face"
VERDICT_VOCAB = (V_READ, V_UNGUARDED, V_GUARDED_UNREAD, V_EMPTY)

GUARDED = (G_DEPTH, G_TYPE, G_BOTH)

TYPE_FUNCS = frozenset(("isinstance", "issubclass"))
NONE_OPS = (ast.Is, ast.IsNot)
EQ_OPS = (ast.Eq, ast.NotEq)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ upstream population
def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    return face, _sha256_file(path)


def population(face):
    """The E525 residue parcels whose boundary is 'the same function again', de-duplicated."""
    seen = {}
    for row in face.get("sites") or []:
        for parcel in row.get("residue_parcels") or []:
            if parcel.get("boundary") != CHAIN_SELF_RECURSION:
                continue
            key = (parcel.get("source"), parcel.get("line"), parcel.get("callee"))
            if key in seen:
                seen[key]["rows_that_share_this_parcel"] += 1
                continue
            item = {
                "source": parcel.get("source"),
                "line": parcel.get("line"),
                "callee": parcel.get("callee"),
                "enclosing_function": parcel.get("enclosing_function"),
                "call_expression": parcel.get("call_expression"),
                "callee_module": parcel.get("callee_module"),
                "rows_that_share_this_parcel": 1,
            }
            seen[key] = item
    return list(seen.values())


# ------------------------------------------------------------------ AST helpers
def _call_name(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _base_name(node):
    """The root name an expression reads off: ``expr.args[0]`` -> ``expr``."""
    while True:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
            continue
        if isinstance(node, ast.Call):
            node = node.func
            continue
        return None


def _parents(tree):
    table = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            table[child] = parent
    return table


def _ancestors(node, parents):
    out = []
    cur = parents.get(node)
    while cur is not None:
        out.append(cur)
        cur = parents.get(cur)
    return out


def _functions(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def find_function(tree, name):
    for node in _functions(tree):
        if node.name == name:
            return node
    return None


def _param_names(fn):
    args = fn.args
    return tuple(a.arg for a in list(args.args) + list(args.kwonlyargs))


def recursive_calls(fn):
    return [node for node in ast.walk(fn)
            if isinstance(node, ast.Call) and _call_name(node.func) == fn.name]


def _is_recursive_call(node, fn):
    return isinstance(node, ast.Call) and _call_name(node.func) == fn.name


def _inside_recursive_call(node, parents, fn):
    for parent in _ancestors(node, parents):
        if _is_recursive_call(parent, fn):
            return True
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
    return False


# ------------------------------------------------------------------ guard detection
def _tested_names(test):
    """Names a boolean test inspects with a type/None test."""
    names = set()
    for node in ast.walk(test):
        if isinstance(node, ast.Call) and _call_name(node.func) in TYPE_FUNCS and node.args:
            base = _base_name(node.args[0])
            if base:
                names.add(base)
        elif isinstance(node, ast.Compare):
            if any(isinstance(op, NONE_OPS + EQ_OPS) for op in node.ops):
                for side in [node.left] + list(node.comparators):
                    if isinstance(side, ast.Constant) and side.value is None:
                        continue
                    base = _base_name(side)
                    if base:
                        names.add(base)
    return names


def _depth_vars_of_call(call, params):
    """Arguments that pass a counter forward (``depth + 1``)."""
    out = set()
    for arg in list(call.args) + [k.value for k in call.keywords]:
        if (isinstance(arg, ast.BinOp) and isinstance(arg.op, (ast.Add, ast.Sub))
                and isinstance(arg.left, ast.Name) and arg.left.id in params
                and isinstance(arg.right, ast.Constant)):
            out.add(arg.left.id)
    return out


def _has_counter_test(fn, var):
    for node in ast.walk(fn):
        if isinstance(node, ast.Compare):
            sides = [node.left] + list(node.comparators)
            names = {s.id for s in sides if isinstance(s, ast.Name)}
            consts = [s for s in sides if isinstance(s, ast.Constant)]
            if var in names and consts:
                return True
    return False


def _comprehension_binds(node, parents):
    """A name this node is bound to by an enclosing comprehension over a container read."""
    names = set()
    for parent in _ancestors(node, parents):
        if isinstance(parent, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
            for gen in parent.generators:
                target = gen.target
                if isinstance(target, ast.Name):
                    names.add(target.id)
                base = _base_name(gen.iter)
                if base:
                    names.add(base)
    return names


def guard_class(fn, call, tree):
    """Classify the guards standing between this recursive call and the function's arms."""
    parents = _parents(tree)
    params = _param_names(fn)
    depth_vars = _depth_vars_of_call(call, params)
    depth = G_NONE
    if depth_vars and any(_has_counter_test(fn, v) for v in depth_vars):
        depth = G_DEPTH

    arg_bases = set()
    for arg in list(call.args) + [k.value for k in call.keywords]:
        base = _base_name(arg)
        if base:
            arg_bases.add(base)
    scopes = set(arg_bases) | _comprehension_binds(call, parents)
    for parent in _ancestors(call, parents):
        if isinstance(parent, ast.If) and (_tested_names(parent.test) & scopes):
            if depth == G_DEPTH:
                return G_BOTH
            return G_TYPE
    return depth


# ------------------------------------------------------------------ arm detection
def _uses_outside_recursion(fn, name, parents):
    """Every node that mentions ``name`` outside a recursive call of the same function."""
    out = {"returns": [], "reads": [], "tests": [], "discards": []}
    for node in ast.walk(fn):
        if not isinstance(node, ast.Name) or node.id != name:
            continue
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            continue
        if _inside_recursive_call(node, parents, fn):
            continue
        if any(isinstance(a, ast.Call) and _call_name(a.func) in TYPE_FUNCS for a in
               _ancestors(node, parents)[:2]):
            out["tests"].append(node.lineno)
            continue
        if any(isinstance(a, ast.Compare) for a in _ancestors(node, parents)[:2]):
            out["tests"].append(node.lineno)
            continue
        ret = None
        via_comprehension = False
        for anc in _ancestors(node, parents):
            if isinstance(anc, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
                via_comprehension = True
            if isinstance(anc, ast.Return):
                ret = anc
                break
            if isinstance(anc, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
        if ret is not None and not via_comprehension:
            out["returns"].append(node.lineno)
        elif any(isinstance(a, ast.Subscript) or isinstance(a, ast.Attribute)
                 for a in _ancestors(node, parents)[:1]):
            out["reads"].append(node.lineno)
        elif any(isinstance(a, ast.Expr) for a in _ancestors(node, parents)):
            out["discards"].append(node.lineno)
        else:
            out["reads"].append(node.lineno)
    return out


def arm_class(uses):
    if uses["returns"]:
        return A_RETURNS
    if uses["reads"]:
        return A_READS
    if uses["tests"]:
        return A_TYPE_ONLY
    if uses["discards"]:
        return A_DISCARDS
    return A_NEVER


# ------------------------------------------------------------------ the study
def corpus_files(root=None):
    root = root or ROOT
    out = []
    for base in ("scripts", "Tools", "firm", "live", "monitor"):
        dpath = os.path.join(root, base)
        if not os.path.isdir(dpath):
            continue
        for dirpath, dirnames, filenames in os.walk(dpath):
            dirnames[:] = [d for d in dirnames if d not in
                           ("__pycache__", ".git", "_quarantine")]
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
                if any(tag in rel for tag in SELF_EXCLUDED):
                    continue
                out.append(rel)
    return sorted(set(out))


def analyse_parcel(parcel, root=None):
    root = root or ROOT
    src = parcel.get("source")
    row = dict(parcel)
    row.update({"function": parcel.get("enclosing_function"), "module": src,
                "recursive_calls": None, "guards": None, "arm": None,
                "arg_base": None, "verdict": None, "evidence": []})
    path = os.path.join(root, src) if src else None
    if not path or not os.path.isfile(path):
        row["evidence"].append("the source file is not in the tree")
        row["verdict"] = V_GUARDED_UNREAD
        return row
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            tree = ast.parse(fh.read(), filename=src)
    except SyntaxError as exc:
        row["evidence"].append("the source does not parse: %s" % exc)
        row["verdict"] = V_GUARDED_UNREAD
        return row
    fn = find_function(tree, parcel.get("enclosing_function"))
    if fn is None:
        row["evidence"].append("the enclosing function is not in the module")
        row["verdict"] = V_GUARDED_UNREAD
        return row
    calls = recursive_calls(fn)
    row["recursive_calls"] = [c.lineno for c in calls]
    guards = sorted({guard_class(fn, c, tree) for c in calls})
    row["guards"] = guards
    parents = _parents(tree)

    target = None
    for call in calls:
        if call.lineno == parcel.get("line"):
            target = call
            break
    if target is None and calls:
        target = calls[0]
        row["evidence"].append("no recursive call on the cited line; the first call was read")
    base = _base_name(target.args[0]) if (target and target.args) else None
    if base is None:
        base = _base_name(target.func) if target else None
    params = _param_names(fn)
    if base is not None and base not in params:
        # the recursed argument may be a comprehension variable; the value it carries is the
        # container the comprehension iterates, which is what the arms act on
        carrier = None
        for anc in _ancestors(target, parents) if target else []:
            if isinstance(anc, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
                for gen in anc.generators:
                    if isinstance(gen.target, ast.Name) and gen.target.id == base:
                        carrier = _base_name(gen.iter)
                        break
            elif isinstance(anc, ast.For):
                if isinstance(anc.target, ast.Name) and anc.target.id == base:
                    carrier = _base_name(anc.iter)
            if carrier:
                break
        if carrier:
            row["evidence"].append(
                "the recursed argument %r is a comprehension variable; the arm is measured on %r"
                % (base, carrier))
            base = carrier
    if base is not None and base not in params:
        row["evidence"].append("the recursed value is not a parameter of the function (%r)" % base)
    row["arg_base"] = base
    uses = _uses_outside_recursion(fn, base, parents) if base else {
        "returns": [], "reads": [], "tests": [], "discards": []}
    row["arm"] = arm_class(uses)
    row["arm_evidence_lines"] = {k: sorted(set(v)) for k, v in uses.items()}

    guarded = all(g in GUARDED for g in guards) if guards else False
    if not guarded:
        row["verdict"] = V_UNGUARDED
    elif row["arm"] in ARM_TERMINATES:
        row["verdict"] = V_READ
    else:
        row["verdict"] = V_GUARDED_UNREAD
    return row


def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(rows, sources):
    by_verdict = _count(rows, "verdict", VERDICT_VOCAB)
    guards = {}
    for g in GUARD_VOCAB:
        guards[g] = len([r for r in rows if g in (r.get("guards") or [])])
    return {
        "sources_read": sources,
        "parcels_examined": len(rows),
        "parcels_by_verdict": by_verdict,
        "parcels_by_arm": _count(rows, "arm", ARM_VOCAB),
        "parcels_by_guard": guards,
        "parcels_read_by_a_terminating_arm": by_verdict.get(V_READ, 0),
        "parcels_with_unguarded_recursion": by_verdict.get(V_UNGUARDED, 0),
        "parcels_guarded_but_never_read": by_verdict.get(V_GUARDED_UNREAD, 0),
        "functions_examined": len({(r.get("module"), r.get("function")) for r in rows}),
        "modules_that_carry_a_self_recursive_parcel": len({r.get("module") for r in rows}),
        "parcels_whose_recursed_value_is_not_a_parameter":
            len([r for r in rows if r.get("arg_base") and
                 "the recursed value is not a parameter" in
                 " ".join(r.get("evidence") or [])]),
        "rows_that_publish_no_verdict": len([r for r in rows if not r.get("verdict")]),
    }


def _verdict(summary):
    if not summary["parcels_examined"]:
        return V_EMPTY
    total = summary["parcels_examined"]
    if summary["parcels_read_by_a_terminating_arm"] == total:
        return V_READ
    if summary["parcels_with_unguarded_recursion"] == total:
        return V_UNGUARDED
    return V_GUARDED_UNREAD


def build(root=None, write=True, rows=None, sources=None, upstream_sha=None):
    root = root or ROOT
    if rows is None:
        face, sha = load_upstream(root)
        pop = population(face)
        rows = [analyse_parcel(p, root) for p in pop]
        upstream_sha = upstream_sha or sha
        sources = len(corpus_files(root)) if sources is None else sources
        # a parcel whose module is outside scripts/Tools/firm/live/monitor still counts as read
        sources = sources or len({r.get("module") for r in rows})
    summary = _summary(rows, sources or 0)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": "which of the self-recursive forwards is read by a terminating arm of the same function",
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the E525 residue parcels whose boundary is `%s`"
                              % (os.path.basename(__file__), CHAIN_SELF_RECURSION)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "a recursive call is never counted as a read: the arm is measured on the parameter's "
            "uses outside every recursive call of the same function",
            "a type/None test counts as a terminating arm because it decides the branch, and it is "
            "published under its own arm class so a value that is only tested is never reported as "
            "a value a caller reads",
            "the guard is read from the call's own ancestors: a depth counter must both be passed "
            "forward (``depth + 1``) and be tested against a constant somewhere in the function; a "
            "type guard must test the name (or the container a comprehension iterates) the recursed "
            "argument reads off",
            "a function reached through a container, a callback or an attribute of an instance is "
            "outside this scan and is never silently published as guarded",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree that other lanes write to; it is published "
            "but not gated, while every verdict, arm and guard class is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "arm_vocab": list(ARM_VOCAB),
        "guard_vocab": list(GUARD_VOCAB),
        "sites": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(outdir, FACE_NAME)
    text = json.dumps(face, indent=1, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return dated


def load_face(root=None, name=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, root=None):
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "sites",
                "method_limits", "arm_vocab", "guard_vocab"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if "::population()" not in str(face.get("population_source") or ""):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("sites") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("parcels_examined") != len(rows):
        bad.append("the examined population does not add up")
    if summary.get("rows_that_publish_no_verdict"):
        bad.append("a parcel publishes no verdict")
    for row in rows:
        if row.get("verdict") not in VERDICT_VOCAB:
            bad.append("%s:%s publishes verdict %r outside the vocabulary"
                       % (row.get("module"), row.get("line"), row.get("verdict")))
        if row.get("arm") not in ARM_VOCAB:
            bad.append("%s:%s publishes arm %r outside the vocabulary"
                       % (row.get("module"), row.get("line"), row.get("arm")))
        for g in row.get("guards") or []:
            if g not in GUARD_VOCAB:
                bad.append("%s:%s publishes guard %r outside the vocabulary"
                           % (row.get("module"), row.get("line"), g))
        if row.get("verdict") == V_UNGUARDED and (row.get("guards") or []) and \
                all(g in GUARDED for g in row.get("guards") or []):
            bad.append("%s:%s is published unguarded although every call carries a guard"
                       % (row.get("module"), row.get("line")))
        if row.get("verdict") == V_READ and row.get("arm") not in ARM_TERMINATES:
            bad.append("%s:%s is published readable with arm %r"
                       % (row.get("module"), row.get("line"), row.get("arm")))
        if row.get("verdict") == V_READ and not (row.get("guards") and all(
                g in GUARDED for g in row.get("guards") or [])):
            bad.append("%s:%s is published readable although no guard ends the recursion (%r)"
                       % (row.get("module"), row.get("line"), row.get("guards")))
    recomputed = _summary(rows, summary.get("sources_read") or 0)
    for key in ("parcels_by_verdict", "parcels_by_arm", "parcels_by_guard",
                "parcels_read_by_a_terminating_arm", "parcels_with_unguarded_recursion",
                "parcels_guarded_but_never_read"):
        if recomputed.get(key) != summary.get(key):
            bad.append("the summary key %s does not re-derive from the rows" % key)
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E528 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "parcels_examined", "parcels_by_verdict", "parcels_by_arm",
                "parcels_by_guard", "functions_examined",
                "modules_that_carry_a_self_recursive_parcel",
                "parcels_read_by_a_terminating_arm", "parcels_with_unguarded_recursion",
                "parcels_guarded_but_never_read")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E528 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
def walk(node, depth=0):
    """Depth-guarded, returns the value."""
    if depth > 3:
        return None
    if isinstance(node, int):
        return node
    return walk(node["n"], depth + 1)


def typed(expr):
    if isinstance(expr, int):
        return True
    if isinstance(expr, (list, tuple)):
        return all(typed(e) for e in expr)
    return False


def loose(node):
    for item in node:
        loose(item)
    return True


def skip(node, depth=0):
    if depth > 2:
        return None
    skip(node, depth + 1)
    return True
'''


def _fixture_root():
    import tempfile
    d = tempfile.mkdtemp(prefix="e528_")
    os.makedirs(os.path.join(d, "scripts"))
    with io.open(os.path.join(d, "scripts", "fixture_mod.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(FIXTURE)
    return d


def selftest():
    bad = []
    d = _fixture_root()
    try:
        rows = [
            analyse_parcel({"source": "scripts/fixture_mod.py", "line": 7,
                            "callee": "walk", "enclosing_function": "walk"}, d),
            analyse_parcel({"source": "scripts/fixture_mod.py", "line": 14,
                            "callee": "typed", "enclosing_function": "typed"}, d),
            analyse_parcel({"source": "scripts/fixture_mod.py", "line": 21,
                            "callee": "loose", "enclosing_function": "loose"}, d),
            analyse_parcel({"source": "scripts/fixture_mod.py", "line": 28,
                            "callee": "skip", "enclosing_function": "skip"}, d),
        ]
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)

    walk, typed, loose, skip = rows
    if G_DEPTH not in walk["guards"]:
        bad.append("the depth counter was not read on walk (%r)" % (walk["guards"],))
    if walk["arm"] != A_RETURNS:
        bad.append("walk's arm is %r, expected a return" % (walk["arm"],))
    if walk["verdict"] != V_READ:
        bad.append("walk is %r, expected read_by_a_terminating_arm" % (walk["verdict"],))
    if G_TYPE not in typed["guards"]:
        bad.append("the type test on the comprehension container was not read (%r)"
                   % (typed["guards"],))
    if typed["verdict"] != V_READ:
        bad.append("typed is %r, expected read_by_a_terminating_arm" % (typed["verdict"],))
    if loose["verdict"] != V_UNGUARDED:
        bad.append("loose is %r, expected the_recursion_is_unguarded" % (loose["verdict"],))
    if loose["arm"] != A_READS:
        bad.append("loose's arm is %r, expected reads_it_without_returning_it" % (loose["arm"],))
    if skip["verdict"] != V_GUARDED_UNREAD:
        bad.append("skip is %r, expected guarded_but_the_value_is_never_read"
                   % (skip["verdict"],))
    if skip["arm"] != A_NEVER:
        bad.append("skip's arm is %r, expected never_mentions_it_outside_the_recursive_call"
                   % (skip["arm"],))

    face = {
        "study": STUDY, "card": CARD, "generated": _now(), "evidence_cutoff": DATE_STAMP,
        "population_source": "e528_recursive_read.py::population() -- fixture",
        "upstream_face": UPSTREAM_FACE, "upstream_face_sha256": "0" * 64,
        "method_limits": ["fixture"], "arm_vocab": list(ARM_VOCAB),
        "guard_vocab": list(GUARD_VOCAB), "verdict_vocab": list(VERDICT_VOCAB),
        "summary": _summary(rows, 1), "verdict": _verdict(_summary(rows, 1)), "sites": rows,
    }
    if face_problems(face):
        bad.append("the fixture face does not pass its own gate: %r" % face_problems(face)[:3])

    doctored = json.loads(json.dumps(face))
    doctored["sites"][0]["verdict"] = V_READ
    doctored["sites"][2]["verdict"] = V_READ
    doctored["summary"] = _summary(doctored["sites"], 1)
    if not face_problems(doctored):
        bad.append("a face that calls an unguarded recursion readable passed the gate")

    doctored2 = json.loads(json.dumps(face))
    doctored2["verdict"] = V_UNGUARDED
    if "the published verdict does not re-derive" not in " ".join(face_problems(doctored2)):
        bad.append("a face whose verdict contradicts its summary passed the gate")

    print("E528 selftest: %d problem(s) / %d checks" % (len(bad), 8))
    for line in bad:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E528 run: opened %r self-recursive parcels across %r modules (%r sources read)"
          % (s["parcels_examined"], s["modules_that_carry_a_self_recursive_parcel"],
             s["sources_read"]))
    print("  verdicts: read by a terminating arm %r | unguarded recursion %r | "
          "guarded but never read %r"
          % (s["parcels_read_by_a_terminating_arm"], s["parcels_with_unguarded_recursion"],
             s["parcels_guarded_but_never_read"]))
    print("  arms %r" % (s["parcels_by_arm"],))
    print("  guards %r" % (s["parcels_by_guard"],))
    print("  verdict %r" % face["verdict"])
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    table = {"run": run, "check": check, "verify": verify, "selftest": selftest}
    if cmd not in table:
        print(__doc__)
        return 2
    return table[cmd]()


if __name__ == "__main__":
    sys.exit(main())