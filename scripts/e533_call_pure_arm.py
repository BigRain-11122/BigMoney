"""E533 -- which open arm's argument is a call that folds to a literal at its own site?

E527 (results/state_tilt/UNDECIDABLEARM-2026-11-08.json) followed one hop out of 52 undecidable
arms and settled 6 with a literal the caller binds.  Four stayed open, and every one of them passes
a *call* or something that is not a value at all.  "Still open" then stands in for two very
different things:

  * the deciding value really is one call further out and that call cannot be evaluated statically
    (it reads a panel, a name, or the tree), and
  * the deciding value is a call whose arguments are literals and whose callee is a pure chain of
    literals -- that call folds to a value, and the arm is decidable at its own site.

This study separates them.  For every open arm E527 published:

  * ``argument_kind`` -- what the argument actually is: a direct call, a name the caller binds from
    a call, a name the caller binds from something else, the caller's own parameter, or an
    expression that is not a call at all.
  * ``fold_class`` -- for a call argument: whether it folds, and if it does not, the first reason
    the fold stopped (an argument that reads a name, a callee that is repo source, a callee the
    fold does not know).
  * ``folded_value`` -- the literal the call folds to, published as text, only when it folds.
  * ``arm_outcome`` -- whether the arm becomes decidable at its own site, or stays open and why.

The fold is a strict whitelist: literals, containers of literals, unary/binary arithmetic over
those, subscripts of a folded container, and calls to a fixed set of builtins whose arguments all
fold.  A name, an attribute read, a comprehension, a slice of a name, or any other callee stops the
fold and is published with the reason rather than guessed at.  Nothing is executed and no source is
rewritten.

    python scripts/e533_call_pure_arm.py build     # write the face
    python scripts/e533_call_pure_arm.py check     # gate the published face (fast)
    python scripts/e533_call_pure_arm.py verify    # re-derive from the tree and gate
    python scripts/e533_call_pure_arm.py selftest  # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e521_reachable_empty_arm as e521  # noqa: E402  (parse_file / find_function)
import e527_undecidable_arm as e527  # noqa: E402  (parent face, open arms, caller bindings)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E533-WHICH-OPEN-ARM-S-ARGUMENT-IS-A-CALL-THAT-IS-ITSELF-PURE-IN-LITERALS-AT-THE-SITE"
STUDY = "E533_call_pure_arm"
DATE_STAMP = "2026-11-08"
FACE_NAME = "callpurearm_latest.json"
DATED_PREFIX = "CALLPUREARM"
PARENT_FACE = "UNDECIDABLEARM-2026-11-08.json"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e533_", "run_e533", "_e533", "CALLPUREARM", "callpurearm_")

OPEN_OUTCOMES = tuple(o for o in e527.ARM_OUTCOME_VOCAB if o not in e527.SETTLED)

# --- what the argument is ---------------------------------------------------------------------
K_DIRECT_CALL = "a_direct_call_at_the_site"
K_NAME_FROM_CALL = "a_name_the_caller_binds_from_a_call"
K_NAME_FROM_OTHER = "a_name_the_caller_binds_from_an_expression_that_is_not_a_call"
K_CALLER_PARAM = "the_caller_function_s_own_parameter"
K_NOT_A_CALL = "an_expression_that_is_not_a_call"
ARGUMENT_KIND_VOCAB = (K_DIRECT_CALL, K_NAME_FROM_CALL, K_NAME_FROM_OTHER, K_CALLER_PARAM, K_NOT_A_CALL)

# --- whether the call folds -------------------------------------------------------------------
F_FOLDS = "the_call_folds_to_a_literal_value"
F_NON_LITERAL_ARG = "the_call_reads_a_name_so_its_arguments_are_not_all_literals"
F_REPO_CALLEE = "the_callee_is_repo_source_and_is_not_inlined_here"
F_UNKNOWN_CALLEE = "the_callee_is_not_a_builtin_this_fold_knows"
F_NOT_A_CALL = "there_is_no_call_to_fold"
FOLD_CLASS_VOCAB = (F_FOLDS, F_NON_LITERAL_ARG, F_REPO_CALLEE, F_UNKNOWN_CALLEE, F_NOT_A_CALL)

# --- per-arm outcome --------------------------------------------------------------------------
O_CLOSED = "the_arm_becomes_decidable_because_the_call_folds_to_a_literal_value"
O_OPEN_READS = "the_arm_stays_open_because_the_call_reads_a_name_rather_than_literals"
O_OPEN_CALLEE = "the_arm_stays_open_because_the_callee_is_not_a_pure_chain_of_literals"
O_NOT_A_CALL = "the_arm_is_out_of_this_population_because_its_argument_is_not_a_call"
ARM_OUTCOME_VOCAB = (O_CLOSED, O_OPEN_READS, O_OPEN_CALLEE, O_NOT_A_CALL)

# --- verdicts ---------------------------------------------------------------------------------
V_EMPTY = "no_open_arm_in_the_population_passes_a_call"
V_ALL_FOLD = "every_open_arm_whose_argument_is_a_call_folds_to_a_literal_value"
V_SOME_FOLD = "a_one_call_fold_closes_some_of_the_call_argument_arms_but_not_all_of_them"
V_NONE_FOLD = "no_open_arm_whose_argument_is_a_call_folds_to_a_literal_value"
VERDICT_VOCAB = (V_EMPTY, V_ALL_FOLD, V_SOME_FOLD, V_NONE_FOLD)

FOLDERS = {
    "range", "list", "tuple", "sorted", "reversed", "len", "sum", "min", "max", "abs", "int",
    "str", "bool", "set", "dict", "round", "divmod", "enumerate", "zip", "any", "all",
}
FOLD_CAP = 256


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _is_self(name):
    return any(name.startswith(prefix) or prefix in name for prefix in SELF_EXCLUDED)


# ------------------------------------------------------------------ population
def load_parent(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", PARENT_FACE), "r", encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """E527's open arms: the ones a literal one hop out did not settle."""
    rows = []
    for site in parent.get("sites", []):
        for arm in site.get("arms") or []:
            if arm.get("arm_class") != e527.ARM_CLASS_OF[e527.ARM_FOLLOWABLE]:
                continue
            if arm.get("arm_outcome") not in OPEN_OUTCOMES:
                continue
            rows.append({"site": site, "arm": arm})
    return rows


# ------------------------------------------------------------------ the fold
class _Stop(Exception):
    def __init__(self, why):
        self.why = why


def _fold(node, depth=0):
    if depth > 12:
        raise _Stop(F_NON_LITERAL_ARG)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_fold(e, depth + 1) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_fold(e, depth + 1) for e in node.elts)
    if isinstance(node, ast.UnaryOp):
        val = _fold(node.operand, depth + 1)
        if isinstance(node.op, ast.USub):
            return -val
        if isinstance(node.op, ast.UAdd):
            return +val
        if isinstance(node.op, ast.Not):
            return not val
        if isinstance(node.op, ast.Invert):
            return ~val
        raise _Stop(F_NON_LITERAL_ARG)
    if isinstance(node, ast.BinOp):
        lft = _fold(node.left, depth + 1)
        rgt = _fold(node.right, depth + 1)
        ops = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
               ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
               ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b,
               ast.Pow: lambda a, b: a ** b, ast.BitOr: lambda a, b: a | b,
               ast.BitAnd: lambda a, b: a & b}
        for op_type, fn in ops.items():
            if isinstance(node.op, op_type):
                try:
                    return fn(lft, rgt)
                except Exception:
                    raise _Stop(F_NON_LITERAL_ARG)
        raise _Stop(F_NON_LITERAL_ARG)
    if isinstance(node, ast.Subscript):
        base = _fold(node.value, depth + 1)
        if isinstance(node.slice, ast.Slice):
            lo = _fold(node.slice.lower, depth + 1) if node.slice.lower is not None else None
            hi = _fold(node.slice.upper, depth + 1) if node.slice.upper is not None else None
            st = _fold(node.slice.step, depth + 1) if node.slice.step is not None else None
            return base[lo:hi:st]
        return base[_fold(node.slice, depth + 1)]
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise _Stop(F_UNKNOWN_CALLEE)
        name = node.func.id
        if name not in FOLDERS:
            raise _Stop(F_UNKNOWN_CALLEE)
        if node.keywords:
            raise _Stop(F_NON_LITERAL_ARG)
        args = [_fold(a, depth + 1) for a in node.args]
        if name == "range":
            if len(args) > 3:
                raise _Stop(F_UNKNOWN_CALLEE)
            out = list(range(*args))
            if len(out) > FOLD_CAP:
                raise _Stop(F_NON_LITERAL_ARG)
            return out
        if name == "reversed":
            return list(reversed(args[0]))
        if name == "sorted":
            return sorted(args[0])
        if name == "enumerate":
            return list(enumerate(*args))
        if name == "zip":
            return list(zip(*args))
        fn = {"list": lambda a: list(a), "tuple": lambda a: tuple(a), "set": lambda a: set(a),
              "dict": lambda *a: dict(*a), "len": lambda a: len(a), "sum": lambda *a: sum(*a),
              "min": lambda *a: min(*a), "max": lambda *a: max(*a), "abs": lambda a: abs(a),
              "int": lambda *a: int(*a), "str": lambda a: str(a), "bool": lambda a: bool(a),
              "round": lambda *a: round(*a), "divmod": lambda a, b: divmod(a, b),
              "any": lambda a: any(a), "all": lambda a: all(a)}[name]
        try:
            return fn(*args)
        except Exception:
            raise _Stop(F_NON_LITERAL_ARG)
    if isinstance(node, ast.Name):
        if node.id in ("True", "False", "None"):
            return {"True": True, "False": False, "None": None}[node.id]
    raise _Stop(F_NON_LITERAL_ARG)


def fold_call(node, root=None):
    """(fold_class, folded_text) for one call node."""
    try:
        value = _fold(node)
    except _Stop as exc:
        reason = exc.why
        if reason == F_UNKNOWN_CALLEE and isinstance(node, ast.Call) and \
                isinstance(node.func, ast.Name) and node.func.id in _repo_functions(root):
            reason = F_REPO_CALLEE
        return reason, None
    return F_FOLDS, _text(value)


_REPO_FN_CACHE = {}


def _repo_functions(root=None):
    """Top-level function names defined anywhere in this repository's scripts/ tree."""
    root = root or ROOT
    if root in _REPO_FN_CACHE:
        return _REPO_FN_CACHE[root]
    names = set()
    for path in corpus_files(root):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except Exception:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
    _REPO_FN_CACHE[root] = names
    return names


def _text(value):
    if isinstance(value, (list, tuple, set)):
        if isinstance(value, set):
            return "set(%r)" % sorted(value)
        inner = ", ".join(_text(v) for v in value)
        if isinstance(value, tuple):
            return "(%s%s)" % (inner, "," if len(value) == 1 else "")
        return "[%s]" % inner
    if isinstance(value, str):
        return repr(value)
    return repr(value)


# ------------------------------------------------------------------ caller side
def _caller_function(tree, line):
    fn = None
    for cand in ast.walk(tree):
        if isinstance(cand, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(cand, "end_lineno", cand.lineno)
            if cand.lineno <= line <= end and (fn is None or cand.lineno > fn.lineno):
                fn = cand
    return fn


def _binding_value(root, caller_rel, line, name):
    """(kind, value_node) for the nearest binding of `name` before `line` in the caller."""
    tree = e521.parse_file(root, caller_rel)
    if tree is None:
        return K_NOT_A_CALL, None
    fn = _caller_function(tree, line)
    if fn is None:
        return K_NOT_A_CALL, None
    bindings = [b for b in e527._bindings(fn) if b[0] == name and b[1] < line]
    if not bindings:
        return K_NOT_A_CALL, None
    params = [b for b in bindings if b[3] == "parameter"]
    if params:
        return K_CALLER_PARAM, None
    nearest = max((b for b in bindings if b[3] != "parameter"), key=lambda b: b[1])
    return K_NAME_FROM_OTHER, nearest[4]


def analyse_arm(row, root=None):
    root = root or ROOT
    site, arm = row["site"], row["arm"]
    expression = arm.get("argument_expression")
    rec = {
        "source": site.get("source"),
        "line": site.get("line"),
        "callee": site.get("callee"),
        "parameter": arm.get("parameter"),
        "argument_expression": expression,
        "e527_binding_class": arm.get("binding_class"),
        "argument_kind": K_NOT_A_CALL,
        "fold_class": F_NOT_A_CALL,
        "folded_value": None,
        "arm_outcome": O_NOT_A_CALL,
        "error": None,
    }
    try:
        node = ast.parse(expression, mode="eval").body
    except Exception as exc:
        rec["error"] = "the_published_argument_expression_does_not_parse: %s" % exc
        return rec

    if isinstance(node, ast.Call):
        rec["argument_kind"] = K_DIRECT_CALL
        fold_class, value = fold_call(node, root)
        rec["fold_class"], rec["folded_value"] = fold_class, value
    elif isinstance(node, ast.Name):
        kind, value_node = _binding_value(root, site.get("source"), site.get("line"), node.id)
        rec["argument_kind"] = kind
        if kind == K_NAME_FROM_CALL or (kind == K_NAME_FROM_OTHER and isinstance(value_node, ast.Call)):
            rec["argument_kind"] = K_NAME_FROM_CALL
            fold_class, value = fold_call(value_node, root)
            rec["fold_class"], rec["folded_value"] = fold_class, value
        elif kind == K_NAME_FROM_OTHER and value_node is not None:
            rec["fold_class"] = F_NOT_A_CALL
    else:
        rec["argument_kind"] = K_NOT_A_CALL

    if rec["fold_class"] == F_FOLDS:
        rec["arm_outcome"] = O_CLOSED
    elif rec["fold_class"] == F_NON_LITERAL_ARG:
        rec["arm_outcome"] = O_OPEN_READS
    elif rec["fold_class"] in (F_REPO_CALLEE, F_UNKNOWN_CALLEE):
        rec["arm_outcome"] = O_OPEN_CALLEE
    else:
        rec["arm_outcome"] = O_NOT_A_CALL
    return rec


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key):
    out = {}
    for row in rows:
        val = row.get(key)
        out[val] = out.get(val, 0) + 1
    return out


def _summary(rows, sources):
    call_arms = [r for r in rows if r.get("argument_kind") in (K_DIRECT_CALL, K_NAME_FROM_CALL)]
    return {
        "sources_read": sources,
        "open_arms_in_parent": len(rows),
        "arms_whose_argument_is_a_call": len(call_arms),
        "arms_closed_by_the_fold": sum(1 for r in rows if r["arm_outcome"] == O_CLOSED),
        "arms_that_stay_open": sum(1 for r in rows if r["arm_outcome"] != O_CLOSED),
        "arms_out_of_scope": sum(1 for r in rows if r["argument_kind"] not in
                                  (K_DIRECT_CALL, K_NAME_FROM_CALL)),
        "arms_by_argument_kind": _count(rows, "argument_kind"),
        "arms_by_fold_class": _count(rows, "fold_class"),
        "arms_by_outcome": _count(rows, "arm_outcome"),
    }


def _verdict(summary):
    if not summary["open_arms_in_parent"]:
        return V_EMPTY
    call_arms = summary["arms_whose_argument_is_a_call"]
    closed = summary["arms_closed_by_the_fold"]
    if not call_arms:
        return V_EMPTY
    if closed == call_arms:
        return V_ALL_FOLD
    if closed == 0:
        return V_NONE_FOLD
    return V_SOME_FOLD


# ------------------------------------------------------------------ face
def corpus_files(root=None):
    root = root or ROOT
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "scripts")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for name in files:
            if name.endswith(".py") and not _is_self(name):
                out.append(os.path.join(base, name))
    return out


def build(root=None, write=True, rows=None, sources=None, parent=None):
    root = root or ROOT
    if rows is None:
        parent = parent or load_parent(root)
        rows = [analyse_arm(r, root) for r in population(parent)]
        if sources is None:
            sources = len(corpus_files(root))
    summary = _summary(rows, sources or 0)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("which open arm's argument is a call that folds to a literal at its own site"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- E527's published arms whose class is the "
                              "followable one and whose outcome is still open" % os.path.basename(__file__)),
        "parent_face": PARENT_FACE,
        "method_limits": [
            "the fold is a strict whitelist: literals, containers of literals, unary/binary "
            "arithmetic over those, subscripts of a folded container, and calls to a fixed set of "
            "builtins whose arguments all fold; anything else stops the fold and is published with "
            "the reason instead of being guessed at",
            "a call to a name defined in this repository is published as repo source rather than "
            "inlined, so 'the callee is not a pure chain of literals' is a statement about what "
            "this fold does, not about the callee's purity",
            "only the four arms E527 left open are examined here; an arm E527 already settled with "
            "a literal one hop out is not re-opened even if its argument is also a call",
            "an arm whose argument is not a call at all is published with its kind and counted as "
            "out of scope rather than dropped, so the population cannot shrink silently",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but "
            "not gated, while every class, every count and the verdict are re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "argument_kind_vocab": list(ARGUMENT_KIND_VOCAB),
        "fold_class_vocab": list(FOLD_CLASS_VOCAB),
        "arm_outcome_vocab": list(ARM_OUTCOME_VOCAB),
        "arms": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for path in (os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)),
                 os.path.join(outdir, FACE_NAME)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return text


def load_face(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", FACE_NAME), "r", encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face):
    problems = []
    rows = face.get("arms") or []
    summary = face.get("summary") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r is not in its own vocabulary" % (face.get("verdict"),))
    if summary.get("open_arms_in_parent") != len(rows):
        problems.append("open_arms_in_parent %r does not equal the published arms %d"
                        % (summary.get("open_arms_in_parent"), len(rows)))
    rec_summary = _summary(rows, summary.get("sources_read") or 0)
    for key in ("arms_whose_argument_is_a_call", "arms_closed_by_the_fold",
                "arms_that_stay_open", "arms_out_of_scope"):
        if summary.get(key) != rec_summary[key]:
            problems.append("%s does not re-derive (%r vs %r)"
                            % (key, summary.get(key), rec_summary[key]))
    for key in ("arms_by_argument_kind", "arms_by_fold_class", "arms_by_outcome"):
        if summary.get(key) != rec_summary[key]:
            problems.append("%s does not re-derive" % key)
    if _verdict(summary) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")

    vocab = {FOLD_CLASS_VOCAB: "fold_class", ARM_OUTCOME_VOCAB: "arm_outcome",
             ARGUMENT_KIND_VOCAB: "argument_kind"}
    for row in rows:
        where = "%s:%s" % (row.get("source"), row.get("line"))
        for allowed, key in vocab.items():
            if row.get(key) not in allowed:
                problems.append("%s: %s %r is not in its vocabulary" % (where, key, row.get(key)))
        if row.get("fold_class") == F_FOLDS:
            if not row.get("folded_value"):
                problems.append("%s: a folding call carries no folded value" % where)
            if row.get("arm_outcome") != O_CLOSED:
                problems.append("%s: a folding call is not published as closing the arm" % where)
        else:
            if row.get("folded_value") is not None:
                problems.append("%s: a non-folding call carries a folded value" % where)
            if row.get("arm_outcome") == O_CLOSED:
                problems.append("%s: an arm was closed without a folded value" % where)
        if row.get("argument_kind") not in (K_DIRECT_CALL, K_NAME_FROM_CALL) and \
                row.get("arm_outcome") != O_NOT_A_CALL:
            problems.append("%s: an arm whose argument is not a call is published as open, not as "
                            "out of scope" % where)
        if row.get("fold_class") == F_NOT_A_CALL:
            if row.get("argument_kind") in (K_DIRECT_CALL, K_NAME_FROM_CALL):
                problems.append("%s: a call argument was published as not a call at all" % where)
    return problems


def check(face=None, root=None):
    face = face if face is not None else load_face(root)
    problems = face_problems(face)
    print(json.dumps({"study": STUDY, "face": FACE_NAME, "problems": problems,
                      "verdict": face.get("verdict"), "arms": len(face.get("arms") or [])},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    live = build(root, write=False)
    published = load_face(root)
    problems = face_problems(live)
    if live.get("arms") != published.get("arms"):
        live_by = {(r["source"], r["line"]): r for r in live["arms"]}
        pub_by = {(r["source"], r["line"]): r for r in published["arms"]}
        missing = sorted(set(live_by) - set(pub_by))
        extra = sorted(set(pub_by) - set(live_by))
        if missing:
            problems.append("the published face is missing %d live arms, e.g. %r"
                            % (len(missing), missing[:3]))
        if extra:
            problems.append("the published face carries %d arms that no longer reproduce, e.g. %r"
                            % (len(extra), extra[:3]))
        for key in sorted(set(live_by) & set(pub_by)):
            if live_by[key] != pub_by[key]:
                problems.append("arm %r re-derives differently (published %r, live %r)"
                                % (key, pub_by[key].get("arm_outcome"),
                                   live_by[key].get("arm_outcome")))
    if live.get("verdict") != published.get("verdict"):
        problems.append("the verdict re-derives to %r, the face publishes %r"
                        % (live.get("verdict"), published.get("verdict")))
    print(json.dumps({"study": STUDY, "problems": problems, "verdict": live.get("verdict"),
                      "arms_live": len(live["arms"]), "arms_published": len(published["arms"])},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE_CALLER = '''\
"""fixture caller."""


def direct_folds():
    return state_table(eff, r6, list(range(3)))


def direct_reads_a_name():
    return state_table(eff, r6, interval(rows, "tight"))


def bound_from_a_call():
    seq_a = list(range(2))
    return state_table(eff, r6, seq_a)


def bound_from_a_comprehension():
    seq_c = [i for i in range(2)]
    return state_table(eff, r6, seq_c)


def bound_from_the_caller_parameter(idxs):
    return state_table(eff, r6, idxs)


def not_a_call(value):
    return state_table(eff, r6, value or [])


def interval(rows, label):
    return (rows[0], rows[-1])
'''


def _fixture_parent(text):
    """A parent face shaped like E527's, pointing at the fixture caller."""
    arms = []
    for marker in ("list(range(3))", "interval(rows, \"tight\")", "seq_a", "seq_c", "idxs",
                   "value or []"):
        arms.append((marker,))
    sites = []
    for idx, (marker,) in enumerate(arms, start=1):
        line = None
        for num, text_line in enumerate(FIXTURE_CALLER.splitlines(), start=1):
            if marker in text_line and "state_table(" in text_line:
                line = num
                break
        sites.append({
            "source": "scripts/fixture_caller.py", "line": line, "callee": "state_table",
            "callee_rel": "scripts/fixture_caller.py", "callee_line": 1,
            "call_expression": "state_table(eff, r6, %s)" % marker,
            "read_kind": "subscripted", "error": None,
            "arms": [{
                "kind": "an_explicit_return_that_names_nothing", "line": 1,
                "arm_class": e527.ARM_CLASS_OF[e527.ARM_FOLLOWABLE],
                "parameter": "idxs",
                "argument_expression": marker,
                "binding_class": "x",
                "arm_outcome": e527.A_NOT_A_NAME,
            }],
            "site_outcome": e527.S_STILL_OPEN, "parameters_followed": ["idxs"],
        })
    return {"sites": sites}


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e533_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        with open(os.path.join(tmp, "scripts", "fixture_caller.py"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE_CALLER)
        parent = _fixture_parent(FIXTURE_CALLER)
        rows = [analyse_arm(r, tmp) for r in population(parent)]
        if len(rows) != 6:
            bad.append("fixture population %d != 6" % len(rows))
        by_expr = {r["argument_expression"]: r for r in rows}
        want = {
            "list(range(3))": (K_DIRECT_CALL, F_FOLDS, O_CLOSED),
            "interval(rows, \"tight\")": (K_DIRECT_CALL, F_REPO_CALLEE, O_OPEN_CALLEE),
            "seq_a": (K_NAME_FROM_CALL, F_FOLDS, O_CLOSED),
            "seq_c": (K_NAME_FROM_OTHER, F_NOT_A_CALL, O_NOT_A_CALL),
            "idxs": (K_CALLER_PARAM, F_NOT_A_CALL, O_NOT_A_CALL),
            "value or []": (K_NOT_A_CALL, F_NOT_A_CALL, O_NOT_A_CALL),
        }
        for expr, (kind, fold_class, outcome) in want.items():
            got = by_expr.get(expr)
            if got is None:
                bad.append("fixture arm %r is missing" % expr)
                continue
            if (got["argument_kind"], got["fold_class"], got["arm_outcome"]) != (kind, fold_class, outcome):
                bad.append("fixture arm %r -> %r != %r"
                           % (expr, (got["argument_kind"], got["fold_class"], got["arm_outcome"]),
                              (kind, fold_class, outcome)))
            if expr == "list(range(3))" and got["folded_value"] != "[0, 1, 2]":
                bad.append("folded value %r != '[0, 1, 2]'" % (got["folded_value"],))
        face = build(tmp, write=False, rows=rows, sources=1)
        problems = face_problems(face)
        if problems:
            bad.append("the fixture face does not gate clean: %r" % (problems[:3],))
        if face["verdict"] != V_SOME_FOLD:
            bad.append("fixture verdict %r != %r" % (face["verdict"], V_SOME_FOLD))
        if face["summary"]["arms_whose_argument_is_a_call"] != 3:
            bad.append("fixture call arms %r != 3"
                       % (face["summary"]["arms_whose_argument_is_a_call"],))
        if face["summary"]["arms_closed_by_the_fold"] != 2:
            bad.append("fixture closed %r != 2" % (face["summary"]["arms_closed_by_the_fold"],))

        def doctored(mutate, why):
            doc = json.loads(json.dumps(face))
            mutate(doc)
            if not face_problems(doc):
                bad.append("a doctored face was accepted: %s" % why)

        doctored(lambda d: d.__setitem__("verdict", V_ALL_FOLD), "hand-written verdict")
        doctored(lambda d: d["summary"].__setitem__("arms_by_outcome", {"x": 1}),
                 "summary counts that do not re-derive")

        def closed_without_value(d):
            for row in d["arms"]:
                if row["arm_outcome"] == O_CLOSED:
                    row["folded_value"] = None
                    return
        doctored(closed_without_value, "an arm closed without a folded value")

        def value_without_fold(d):
            for row in d["arms"]:
                if row["fold_class"] != F_FOLDS:
                    row["folded_value"] = "[1]"
                    return
        doctored(value_without_fold, "a folded value on a call that did not fold")

        def not_a_call_but_open(d):
            for row in d["arms"]:
                if row["argument_kind"] == K_CALLER_PARAM:
                    row["arm_outcome"] = O_OPEN_READS
                    return
        doctored(not_a_call_but_open, "an out-of-scope arm published as open")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(json.dumps({"study": STUDY, "selftest": "green" if not bad else "red",
                      "problems": bad}, ensure_ascii=False, indent=1))
    return 0 if not bad else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"face": FACE_NAME, "arms": len(face["arms"]),
                          "verdict": face["verdict"], "summary": face["summary"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (build|check|verify|selftest)" % cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())