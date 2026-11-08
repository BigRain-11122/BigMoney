"""E558 -- would a --check gate leg notice its face going missing?

E557 (r1583) found three of the four writers of E556's message-only faces are named
by a live chain leg only with ``--check``: the leg proves the face is still right but
can never rebuild it.  The next question is whether that gate would even *notice* the
loss, and that is a different measurement from "does the leg rebuild it".

For each of the gate legs E557 published (machine-read from its face, never retyped)
this study follows the gate verb's own entry path -- ``main()`` -> the branch on the
``--check`` flag -> every local function that branch calls, transitively -- and asks
two static questions about that function set:

  * does it ever LOAD the face the leg gates (an ``open``/``read_text``/``json.load``
    whose argument folds to the face path through the module's own constants)?
  * is a missing file REFUSED (an explicit ``if not <face>.exists(): return 1`` /
    ``raise SystemExit``, or an ``except FileNotFoundError/OSError`` that returns
    non-zero or raises)?  An unguarded load is published as a separate class: the
    process still ends non-zero, but by an uncaught traceback, not by a refusal.

The classes the earlier arms could not separate:

  * the gate reads the face and refuses a missing one        (detection, graceful)
  * the gate reads the face but a missing one is not refused (reads a face that may
    already be gone and passes)
  * the gate never opens the face -- its absence is invisible by construction
  * the gate opens a path this scan cannot fold -- unassessable, not silent

A third arm is measured because a refusal that nothing carries is not detection: the
chain runner's own handling of a leg's return code (does the process exit non-zero
when a leg fails, or is the failure only printed into a receipt?).

    python scripts/e558_gate_reach.py build      # publish the face
    python scripts/e558_gate_reach.py check      # re-derive from source; problems must be []
    python scripts/e558_gate_reach.py verify     # two builds identical
    python scripts/e558_gate_reach.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e554_wrote_population as e554  # noqa: E402  (corpus + the path folder's vocabulary)
import e557_face_entry_reach as e557  # noqa: E402  (the population this extends)

STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "gateread_latest.json")
DATED_PREFIX = "GATEREAD"
PARENT = os.path.join(STATE_TILT, "faceentryreach_latest.json")

STUDY = "E558"
CARD = "E558"
TITLE = "whether a --check gate leg reads the face it gates and can notice its absence"
EVIDENCE_CUTOFF = "2026-11-08"
MACHINE = "bm-b"

# ---- outcomes -------------------------------------------------------------
G_REFUSED = "the_gate_reads_the_face_and_refuses_a_missing_one"
G_CRASH = "the_gate_reads_the_face_and_a_missing_one_would_raise_an_uncaught_error"
G_NOT_REFUSED = "the_gate_reads_the_face_but_a_missing_one_is_not_refused"
G_INVISIBLE = "the_gate_never_opens_the_face_so_a_missing_one_is_invisible"
G_UNFOLDABLE = "the_gate_opens_a_path_this_scan_cannot_fold"
G_NO_ENTRY = "the_gate_entry_function_cannot_be_followed_from_the_check_flag"

OUTCOME_VOCAB = (G_REFUSED, G_CRASH, G_NOT_REFUSED, G_INVISIBLE, G_UNFOLDABLE, G_NO_ENTRY)
REFUSING_OUTCOMES = (G_REFUSED,)
NOTICING_OUTCOMES = (G_REFUSED, G_CRASH)
NOT_NOTICING_OUTCOMES = (G_INVISIBLE, G_NOT_REFUSED, G_UNFOLDABLE, G_NO_ENTRY)

V_INVISIBLE = "some_gated_faces_would_vanish_without_their_gate_noticing"
V_NOT_REFUSED = "every_gate_opens_its_face_but_some_do_not_refuse_a_missing_one"
V_CRASH_ONLY = "every_gate_would_fail_on_a_missing_face_but_only_by_an_uncaught_error"
V_REFUSED = "every_gate_reads_its_face_and_refuses_a_missing_one"

# ---- load-call vocabulary -------------------------------------------------
LOAD_ATTRS = ("read_text", "read_bytes", "read_json", "read_csv", "read_parquet",
              "read_excel", "loadtxt", "load")
LOAD_FUNCS = ("open", "load", "loads", "read_csv", "read_parquet", "read_json",
              "read_text", "read_bytes")
MISSING_FILE_ERRORS = ("FileNotFoundError", "OSError", "IOError", "Exception")

GATE_FLAG = "--check"


def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


# ---------------------------------------------------------------- population
def population():
    """Every ``(face, writer, gate leg)`` E557 published, read out of E557's face.

    E557 counted five gate-leg rows over three writers; two of the legs serve two
    faces each, so the row count and the leg count are published separately.
    """
    parent = json.load(io.open(PARENT, encoding="utf-8"))
    out = []
    for r in parent.get("rows") or []:
        for s in r.get("gate_entry_points") or []:
            if s.get("kind") != e557.N_CHAIN_GATE:
                continue
            out.append({
                "face": r.get("face"),
                "writer": r.get("writer"),
                "gate_source": s.get("source"),
                "gate_leg": s.get("leg"),
                "gate_argv": list(s.get("argv") or []),
                "gate_machine": s.get("machine"),
                "also_run_by": list(s.get("also_run_by") or []),
                "reach_class": r.get("reach_class"),
            })
    out.sort(key=lambda r: (r["writer"], r["face"], r["gate_source"]))
    return out


def distinct_legs():
    seen = []
    for r in population():
        key = (r["gate_source"], r["gate_leg"])
        if key not in seen:
            seen.append(key)
    return seen


def writers():
    seen = []
    for r in population():
        if r["writer"] not in seen:
            seen.append(r["writer"])
    return sorted(seen)


# ---------------------------------------------------------------- path folding
def _norm(v):
    v = v.replace("\\", "/")
    while v.startswith("./"):
        v = v[2:]
    if v == ".":
        return ""
    return v


def _foldp(expr, consts, depth=0):
    """A path expression as a repo-relative string, or ``(None, why)``.

    ``e554._fold`` folds plain strings, ``os.path.join`` and ``ROOT / "a" / "b"``,
    but five of the writers in this family spell their faces with
    ``Path(__file__).resolve().parents[1]`` -- a ``Path`` chain ``_fold`` stops at,
    which would publish every one of their faces as "never opened".  So the Path
    methods are folded here instead of being inherited.
    """
    if depth > 10 or expr is None:
        return None, "no_expression"
    if isinstance(expr, ast.Constant):
        if isinstance(expr.value, str):
            return _norm(expr.value), None
        return None, "not_a_string"
    if isinstance(expr, ast.Name):
        if expr.id in consts:
            return consts[expr.id], None
        if expr.id in ("ROOT", "HERE", "__file__"):
            return "", None
        return None, "name_this_scan_cannot_fold"
    if isinstance(expr, ast.BinOp):
        left, why = _foldp(expr.left, consts, depth + 1)
        right, why2 = _foldp(expr.right, consts, depth + 1)
        if left is None:
            return None, why
        if right is None:
            return None, why2
        if isinstance(expr.op, ast.Add):
            return _norm(left + right), None
        if isinstance(expr.op, ast.Div):
            return _norm(os.path.join(left, right)), None
        return None, "runtime_expression"
    if isinstance(expr, ast.Attribute):
        if expr.attr == "parent":
            base, why = _foldp(expr.value, consts, depth + 1)
            return (None, why) if base is None else (_norm(os.path.dirname(base)), None)
        if expr.attr == "parents":
            return None, "subscripted_parents"
        # a plain attribute of a folded path (``p.parents[0]`` handled above)
        return _foldp(expr.value, consts, depth + 1)
    if isinstance(expr, ast.Subscript):
        if isinstance(expr.value, ast.Attribute) and expr.value.attr == "parents":
            base, why = _foldp(expr.value.value, consts, depth + 1)
            idx = expr.slice
            if base is None:
                return None, why
            if isinstance(idx, ast.Constant) and isinstance(idx.value, int):
                out = base
                for _ in range(idx.value):
                    out = os.path.dirname(out)
                return _norm(out), None
            return None, "subscripted_parents"
        return None, "subscripted_path"
    if isinstance(expr, ast.Call):
        leaf = e554._leaf(expr.func)
        if leaf in ("Path", "PurePath", "str", "resolve", "abspath"):
            arg = expr.args[0] if expr.args else None
            if leaf in ("resolve", "abspath") and isinstance(expr.func, ast.Attribute):
                arg = expr.func.value
            return _foldp(arg, consts, depth + 1)
        if leaf == "join":
            parts = []
            for a in expr.args:
                val, why = _foldp(a, consts, depth + 1)
                if val is None:
                    return None, why
                if val in ("", "."):
                    continue
                parts.append(val)
            if not parts:
                return "", None
            joined = parts[0]
            for p in parts[1:]:
                joined = os.path.join(joined, p)
            return _norm(joined), None
        if leaf == "dirname":
            base, why = _foldp(expr.args[0] if expr.args else None, consts, depth + 1)
            return (None, why) if base is None else (_norm(os.path.dirname(base)), None)
        if leaf in ("as_posix", "relative_to", "with_suffix", "replace"):
            target = expr.func.value if isinstance(expr.func, ast.Attribute) else (
                expr.args[0] if expr.args else None)
            base, why = _foldp(target, consts, depth + 1)
            if base is None:
                return None, why
            if leaf == "with_suffix" and expr.args and isinstance(expr.args[0], ast.Constant):
                stem, _old = os.path.splitext(base)
                return _norm(stem + str(expr.args[0].value)), None
            return base, None
        return None, "runtime_expression"
    return None, "runtime_expression"


def _consts(tree):
    """Module-level ``NAME = <path expression>``, folded in declaration order."""
    consts = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.value is not None:
            name, value = node.target.id, node.value
        else:
            continue
        val, _why = _foldp(value, consts)
        if val is not None:
            consts[name] = val
    return consts


# ---------------------------------------------------------------- gate entry
def _find_func(tree, name):
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _argparse_dest(tree):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        flags = [a.value for a in node.args
                 if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if GATE_FLAG not in flags:
            continue
        for kw in node.keywords:
            if kw.arg == "dest" and isinstance(kw.value, ast.Constant):
                return str(kw.value.value)
        return GATE_FLAG.lstrip("-")
    return None


def _mentions_flag(test, dest):
    for node in ast.walk(test):
        if isinstance(node, ast.Attribute) and node.attr == dest:
            return True
        if isinstance(node, ast.Name) and node.id == dest:
            return True
        if isinstance(node, ast.Constant) and node.value == GATE_FLAG:
            return True
    return False


def _gate_entry(tree, max_depth=4):
    """The functions the ``--check`` flag reaches from ``main()``.

    ``main()`` branches on the flag (``if args.check or args.cmd == "check":
    return check()``), so the entry path is that branch plus every local function
    it calls, followed transitively -- a guard that lives in ``check_payload`` is
    reached by the flag just as surely as one in ``check`` itself.
    """
    dest = _argparse_dest(tree)
    if dest is None:
        return {"resolved": False,
                "why": "no argparse argument declares %s" % GATE_FLAG,
                "dest": None, "names": [], "bodies": []}
    main_fn = _find_func(tree, "main")
    if main_fn is None:
        return {"resolved": False, "why": "there is no main()", "dest": dest,
                "names": [], "bodies": []}
    branches = [n for n in ast.walk(main_fn)
                if isinstance(n, ast.If) and _mentions_flag(n.test, dest)]
    if not branches:
        return {"resolved": False,
                "why": "main() never branches on the %s flag" % GATE_FLAG,
                "dest": dest, "names": [], "bodies": []}
    frontier = []
    for b in branches:
        for n in ast.walk(b):
            if isinstance(n, ast.Call):
                leaf = e554._leaf(n.func)
                if leaf and leaf not in frontier:
                    frontier.append(leaf)
    names, bodies = [], []
    for _depth in range(max_depth):
        nxt = []
        for name in frontier:
            if name in names:
                continue
            fn = _find_func(tree, name)
            if fn is None:
                continue
            names.append(name)
            bodies.append(fn)
            for n in ast.walk(fn):
                if isinstance(n, ast.Call):
                    leaf = e554._leaf(n.func)
                    if leaf and leaf not in names and leaf not in nxt:
                        nxt.append(leaf)
        frontier = nxt
        if not frontier:
            break
    return {"resolved": bool(bodies), "why": None if bodies else
            "the flag branch calls no local function this scan can follow",
            "dest": dest, "names": names, "bodies": bodies}


# ---------------------------------------------------------------- loads
def _is_write_mode(call):
    for a in list(call.args[1:]) + [kw.value for kw in call.keywords if kw.arg == "mode"]:
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            if any(ch in a.value for ch in ("w", "a", "x")):
                return True
    return False


def _bound_paths(fn, consts):
    """Names in a function bound to a folded path by ``open``.

    ``with open(OUT_JSON) as fh: payload = json.load(fh)`` names the face in the
    ``open`` call, so a scan that only folds ``json.load``'s argument sees a name it
    cannot resolve and publishes a face that IS read as never opened.
    """
    bound = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.optional_vars, ast.Name) and isinstance(
                        item.context_expr, ast.Call):
                    leaf = e554._leaf(item.context_expr.func)
                    if leaf == "open" and item.context_expr.args:
                        val, _why = _foldp(item.context_expr.args[0], consts)
                        if val is not None:
                            bound[item.optional_vars.id] = val
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call):
            leaf = e554._leaf(node.value.func)
            if leaf == "open" and node.value.args:
                val, _why = _foldp(node.value.args[0], consts)
                if val is not None:
                    bound[node.targets[0].id] = val
    return bound


def _load_target(call, bound, consts):
    """The path expression a load call reads, plus how it was spelled."""
    leaf = e554._leaf(call.func)
    if leaf == "open":
        if _is_write_mode(call):
            return None, "write_mode"
        return (call.args[0] if call.args else None), "open"
    if leaf in ("read_text", "read_bytes"):
        return call.func.value, leaf
    if leaf in ("load", "loads", "read_csv", "read_parquet", "read_json"):
        if leaf == "loads":
            return None, "parses_a_string_not_a_file"
        arg = call.args[0] if call.args else None
        if isinstance(arg, ast.Name) and arg.id in bound:
            return ast.Constant(value=bound[arg.id]), "%s_of_a_with_bound_handle" % leaf
        return arg, leaf
    return None, "not_a_loader"


def _loads(bodies, consts):
    out = []
    for fn in bodies:
        bound = _bound_paths(fn, consts)
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            target, how = _load_target(node, bound, consts)
            if target is None:
                if how == "write_mode":
                    continue
                if how == "parses_a_string_not_a_file":
                    continue
                if how == "not_a_loader":
                    continue
                out.append({"function": fn.name, "line": node.lineno, "how": how,
                            "path": None, "why": "no_argument",
                            "expression": _src(node)})
                continue
            path, why = _foldp(target, consts)
            out.append({"function": fn.name, "line": node.lineno, "how": how,
                        "path": path, "why": why, "expression": _src(node)})
    out.sort(key=lambda r: (r["function"], r["line"]))
    return out


def _src(node):
    try:
        return ast.unparse(node)[:200]
    except Exception:
        return ""


# ---------------------------------------------------------------- refusals
def _exists_test(test, consts):
    """``(path, negated)`` for a missing-file test, or ``None``.

    Recognised: ``not X.exists()``, ``not os.path.exists(X)``,
    ``not os.path.isfile(X)``, ``X.is_file() == False`` -- the shapes the tree uses.
    """
    for node in ast.walk(test):
        if not isinstance(node, ast.UnaryOp) or not isinstance(node.op, ast.Not):
            continue
        inner = node.operand
        if isinstance(inner, ast.Call):
            leaf = e554._leaf(inner.func)
            if leaf == "exists" and isinstance(inner.func, ast.Attribute):
                path, why = _foldp(inner.func.value, consts)
                if path is not None:
                    return path, True, why
            if leaf in ("exists", "isfile", "isdir", "lexists") and inner.args:
                path, why = _foldp(inner.args[0], consts)
                if path is not None:
                    return path, True, why
    for node in ast.walk(test):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 \
                and isinstance(node.ops[0], (ast.Is, ast.Eq)) \
                and any(isinstance(c, ast.Constant) and c.value is False
                        for c in node.comparators):
            left = node.left
            leaf = e554._leaf(left.func) if isinstance(left, ast.Call) else ""
            if leaf in ("exists", "isfile") and isinstance(left, ast.Call):
                target = left.func.value if isinstance(left.func, ast.Attribute) else (
                    left.args[0] if left.args else None)
                path, why = _foldp(target, consts)
                if path is not None:
                    return path, True, why
    return None


def _exit_kind(stmts):
    """What a branch does when it fires: refuse (non-zero) or fall through."""
    kinds = []
    for st in stmts:
        for node in ast.walk(st):
            if isinstance(node, ast.Return):
                v = node.value
                if isinstance(v, ast.Constant) and isinstance(v.value, int) and v.value != 0:
                    kinds.append("returns_non_zero")
                elif v is None or (isinstance(v, ast.Constant) and v.value in (0, None)):
                    kinds.append("returns_zero_or_nothing")
                else:
                    kinds.append("returns_a_value")
            elif isinstance(node, ast.Raise):
                kinds.append("raises")
            elif isinstance(node, ast.Call) and e554._leaf(node.func) == "exit":
                a = node.args[0] if node.args else None
                if isinstance(a, ast.Constant) and a.value not in (0, None):
                    kinds.append("exits_non_zero")
    for want in ("returns_non_zero", "raises", "exits_non_zero"):
        if want in kinds:
            return want
    if "returns_zero_or_nothing" in kinds:
        return "returns_zero_or_nothing"
    if "returns_a_value" in kinds:
        return "returns_a_value"
    return "does_not_refuse"


REFUSING_EXITS = ("returns_non_zero", "raises", "exits_non_zero")


def _guards(bodies, consts, face_rel, face_loads):
    """Every missing-file branch the gate set contains, and whether it is about the face."""
    out = []
    for fn in bodies:
        for node in ast.walk(fn):
            if isinstance(node, ast.If):
                got = _exists_test(node.test, consts)
                if got is None:
                    continue
                path, negated, _why = got
                out.append({"kind": "explicit_missing_file_branch",
                            "function": fn.name, "line": node.lineno,
                            "about_the_gated_face": path == face_rel,
                            "path": path, "negated": negated,
                            "exit": _exit_kind(node.body),
                            "expression": _src(node.test)})
            elif isinstance(node, ast.Try):
                catches = []
                for h in node.handlers:
                    types = []
                    if h.type is None:
                        types = ["bare_except"]
                    elif isinstance(h.type, ast.Tuple):
                        types = [e554._leaf(t) for t in h.type.elts]
                    elif isinstance(h.type, ast.Name):
                        types = [h.type.id]
                    if any(t in MISSING_FILE_ERRORS for t in types):
                        catches.append({"types": types, "exit": _exit_kind(h.body),
                                        "line": h.lineno})
                if not catches:
                    continue
                body_loads = []
                for st in node.body:
                    for n in ast.walk(st):
                        if isinstance(n, ast.Call):
                            target, how = _load_target(n, _bound_paths(fn, consts), consts)
                            if target is None:
                                continue
                            path, _why = _foldp(target, consts)
                            if path == face_rel:
                                body_loads.append(n.lineno)
                out.append({"kind": "except_catches_missing_file",
                            "function": fn.name, "line": node.lineno,
                            "about_the_gated_face": bool(body_loads),
                            "path": face_rel if body_loads else None,
                            "catches": catches,
                            "loads_the_face_at": body_loads,
                            "exit": ",".join(sorted({c["exit"] for c in catches})),
                            "expression": "try/except %s" % "/".join(
                                sorted({t for c in catches for t in c["types"]}))})
    out.sort(key=lambda r: (r["function"], r["line"]))
    return out


# ---------------------------------------------------------------- classify
def classify(entry, loads, guards):
    if not entry.get("resolved"):
        return G_NO_ENTRY, "the gate entry could not be followed: %s" % entry.get("why")
    about = [g for g in guards if g["about_the_gated_face"]]
    refusing = [g for g in about if g["exit"] in REFUSING_EXITS]
    if refusing:
        return G_REFUSED, "a missing file is refused at line %s (%s)" % (
            refusing[0]["line"], refusing[0]["exit"])
    if about:
        return G_NOT_REFUSED, ("a missing-file branch exists at line %s and does not "
                               "return non-zero (%s)" % (about[0]["line"], about[0]["exit"]))
    face_loads = [l for l in loads if l["path"] is not None and l["path"] == _FACE[0]]
    if face_loads:
        return G_CRASH, ("the face is opened at line %s with no missing-file guard, so a "
                         "deleted face ends the leg in a traceback"
                         % face_loads[0]["line"])
    unfoldable = [l for l in loads if l["path"] is None and l["why"] != "no_argument"]
    if unfoldable:
        return G_UNFOLDABLE, ("a loader at line %s reads a path this scan cannot fold (%s)"
                              % (unfoldable[0]["line"], unfoldable[0]["why"]))
    return G_INVISIBLE, "no load in the gate path opens this face"


# ``classify`` is called per row; the face under test is carried in a one-slot box so
# the function stays a pure three-argument classifier for the fixtures.
_FACE = [None]


def classify_face(entry, loads, guards, face_rel):
    _FACE[0] = face_rel
    try:
        return classify(entry, loads, guards)
    finally:
        _FACE[0] = None


# ---------------------------------------------------------------- runner arm
def runner_arm(chain_rel):
    """Does the chain runner's own process exit carry a failing leg?

    All three runners record each leg's return code, print the non-zero ones and
    write a receipt.  If ``main`` then returns 0, the refusal is only a line in a
    receipt -- nothing on the machine's exit path says the gate failed.
    """
    text = e554._corpus().get(chain_rel) or ""
    if not text:
        return {"chain": chain_rel, "readable": False,
                "process_exit_carries_the_failure": None,
                "why": "the chain source is not in the corpus"}
    try:
        tree = ast.parse(text.lstrip("\ufeff"))
    except SyntaxError:
        return {"chain": chain_rel, "readable": False,
                "process_exit_carries_the_failure": None,
                "why": "the chain source does not parse"}
    records = False
    compares = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "returncode":
            records = True
        if isinstance(node, ast.Compare) and len(node.ops) == 1 \
                and isinstance(node.ops[0], (ast.NotEq, ast.Gt)):
            right = node.comparators[0]
            if isinstance(right, ast.Constant) and right.value == 0:
                left = node.left
                if isinstance(left, ast.Name) and left.id in ("rc", "returncode"):
                    compares = True
                if isinstance(left, ast.Subscript) and isinstance(left.slice, ast.Constant) \
                        and left.slice.value == "rc":
                    compares = True
    main_fn = _find_func(tree, "main")
    bad_line = None
    if main_fn is not None:
        for node in ast.walk(main_fn):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and node.targets[0].id in ("bad", "failed", "fails"):
                bad_line = node.lineno
    exits = []
    carries = False
    if main_fn is not None and bad_line is not None:
        for node in ast.walk(main_fn):
            if isinstance(node, ast.Return) and node.lineno > bad_line:
                v = node.value
                if isinstance(v, ast.Constant) and isinstance(v.value, int):
                    exits.append({"line": node.lineno, "value": v.value,
                                  "returns_a_constant": True})
                    if v.value != 0:
                        carries = True
                else:
                    exits.append({"line": node.lineno, "value": None,
                                  "returns_a_constant": False})
            if isinstance(node, ast.Raise) and node.lineno > bad_line:
                exits.append({"line": node.lineno, "value": "raise",
                              "returns_a_constant": False})
                carries = True
            if isinstance(node, ast.Call) and node.lineno > bad_line \
                    and e554._leaf(node.func) == "exit":
                a = node.args[0] if node.args else None
                if isinstance(a, ast.Constant) and a.value not in (0, None):
                    exits.append({"line": node.lineno, "value": "sys.exit(%s)" % a.value,
                                  "returns_a_constant": True})
                    carries = True
    return {"chain": chain_rel,
            "readable": True,
            "records_each_legs_return_code": records,
            "compares_a_return_code_against_zero": compares,
            "prints_the_non_zero_legs": "NONZERO" in text,
            "failing_legs_are_collected_after_line": bad_line,
            "what_main_returns_after_that": exits,
            "process_exit_carries_the_failure": carries,
            "note": ("carries is read as: any return/raise/sys.exit after the failing-legs "
                     "list is built and whose value is non-zero; a plain `return 0`, or "
                     "no return at all (the function falls off the end), does not carry")}


# ---------------------------------------------------------------- control arm
CONTROL_GATE = "scripts/etf_book_hysteresis.py"


def _control_specs():
    return (CONTROL_GATE, "results/etf_book_hysteresis.json",
            "results/etf_book_hysteresis.md")


def measure_source(source_text, face_rel):
    """The full pipeline over one source string, used by build() and the selftest."""
    tree = ast.parse(source_text.lstrip("\ufeff"))
    consts = _consts(tree)
    entry = _gate_entry(tree)
    loads = _loads(entry["bodies"], consts)
    guards = _guards(entry["bodies"], consts, face_rel, loads)
    outcome, why = classify_face(entry, loads, guards, face_rel)
    return {"entry": entry, "loads": loads, "guards": guards,
            "outcome": outcome, "why": why, "consts": consts}


def _control_arm():
    """One writer, two faces, opposite answers -- the census must tell them apart.

    ``etf_book_hysteresis`` gates ``results/etf_book_hysteresis.json`` (and refuses a
    missing one) while it *writes* ``results/etf_book_hysteresis.md`` and never opens
    it.  If the census cannot see the difference inside a single module, a reading of
    "this face is invisible" would be the instrument's blindness.
    """
    src = e554._corpus().get(CONTROL_GATE) or ""
    gate_face, render_face = _control_specs()[1], _control_specs()[2]
    if not src:
        return {"found": False, "why": "%s is not in the corpus" % CONTROL_GATE}
    g = measure_source(src, gate_face)
    r = measure_source(src, render_face)
    found = g["outcome"] == G_REFUSED and r["outcome"] == G_INVISIBLE
    why = None
    if not found:
        if g["outcome"] != G_REFUSED:
            why = ("the control gate's own face is read as %r, so 'a missing face is "
                   "refused' is not distinguishable from a blind scan" % g["outcome"])
        else:
            why = ("the render the same module writes is read as %r, so 'never opened' "
                   "is not distinguishable from 'opened but unfollowed'"
                   % r["outcome"])
    return {"found": found, "why": why,
            "module": CONTROL_GATE,
            "face_that_must_be_refused": gate_face,
            "face_that_must_be_invisible": render_face,
            "outcomes": {gate_face: g["outcome"], render_face: r["outcome"]},
            "entry_functions": g["entry"]["names"],
            "why_refused": g["why"]}


# ---------------------------------------------------------------- build
def _face_kind(face_rel):
    ext = os.path.splitext(face_rel)[1].lower()
    if ext == ".json":
        return "machine_readable_face"
    if ext in (".md", ".txt"):
        return "rendered_face_a_human_reads"
    return "other"


def build(write=True):
    rows = []
    cache = {}
    for r in population():
        writer = r["writer"]
        if writer not in cache:
            src = e554._corpus().get(writer)
            if src is None and os.path.isfile(os.path.join(ROOT, writer)):
                src = _read(os.path.join(ROOT, writer))
            cache[writer] = src
        src = cache[writer] or ""
        m = measure_source(src, r["face"]) if src else {
            "entry": {"resolved": False, "why": "the writer source is not in the corpus",
                      "names": [], "bodies": []},
            "loads": [], "guards": [], "outcome": G_NO_ENTRY,
            "why": "the writer source is not in the corpus"}
        rows.append({
            "face": r["face"],
            "face_kind": _face_kind(r["face"]),
            "writer": writer,
            "writer_in_corpus": bool(src),
            "gate_source": r["gate_source"],
            "gate_leg": r["gate_leg"],
            "gate_argv": r["gate_argv"],
            "gate_machine": r["gate_machine"],
            "also_run_by": r["also_run_by"],
            "reach_class": r["reach_class"],
            "gate_entry": {"resolved": m["entry"].get("resolved"),
                           "why": m["entry"].get("why"),
                           "functions": m["entry"].get("names") or [],
                           "flag_dest": m["entry"].get("dest")},
            "loads": m["loads"],
            "missing_file_guards": m["guards"],
            "outcome": m["outcome"],
            "why": m["why"],
            "would_a_deleted_face_be_detected": m["outcome"] in NOTICING_OUTCOMES,
            "would_a_deleted_face_be_refused": m["outcome"] in REFUSING_OUTCOMES,
        })
    rows.sort(key=lambda r: (r["writer"], r["face"], r["gate_source"]))

    control = _control_arm()
    if not control["found"]:
        raise SystemExit("the gate census is blind: %s" % control["why"])

    by_outcome = {c: 0 for c in OUTCOME_VOCAB}
    for r in rows:
        by_outcome[r["outcome"]] += 1

    by_writer = {}
    for r in rows:
        w = by_writer.setdefault(r["writer"], {
            "writer": r["writer"], "faces": [], "outcomes": {},
            "legs": [], "gate_entry_functions": r["gate_entry"]["functions"]})
        w["faces"].append(r["face"])
        w["outcomes"][r["face"]] = r["outcome"]
        w.setdefault("paths_its_gate_opens", set()).update(
            l["path"] for l in r["loads"] if l.get("path"))
        if r["gate_leg"] not in w["legs"]:
            w["legs"].append(r["gate_leg"])
    for w in by_writer.values():
        w["faces"].sort()
        w["legs"].sort()
        w["paths_its_gate_opens"] = sorted(w.get("paths_its_gate_opens") or [])
        w["every_face_refused"] = all(c == G_REFUSED for c in w["outcomes"].values())
        w["any_face_invisible"] = any(c == G_INVISIBLE for c in w["outcomes"].values())

    chains = sorted({r["gate_source"] for r in rows})
    runners = [runner_arm(c) for c in chains]

    n_refused = by_outcome[G_REFUSED]
    n_crash = by_outcome[G_CRASH]
    n_not_refused = by_outcome[G_NOT_REFUSED]
    n_invisible = by_outcome[G_INVISIBLE]
    if n_invisible:
        verdict = V_INVISIBLE
    elif n_not_refused:
        verdict = V_NOT_REFUSED
    elif n_crash:
        verdict = V_CRASH_ONLY
    else:
        verdict = V_REFUSED

    machine_faces = [r for r in rows if r["face_kind"] == "machine_readable_face"]
    render_faces = [r for r in rows if r["face_kind"] == "rendered_face_a_human_reads"]
    population_faces = {r["face"] for r in rows}
    gated_but_not_in_the_population = sorted({
        p for w in by_writer.values() for p in w["paths_its_gate_opens"]
        if _face_kind(p) == "machine_readable_face" and p not in population_faces})

    summary = {
        "row_leg_pairs": len(rows),
        "distinct_gate_legs": len({(r["gate_source"], r["gate_leg"]) for r in rows}),
        "distinct_writers": len(by_writer),
        "rows_whose_gate_entry_could_be_followed": sum(
            1 for r in rows if r["gate_entry"]["resolved"]),
        "rows_a_deleted_face_would_be_refused": n_refused,
        "rows_a_deleted_face_would_only_crash": n_crash,
        "rows_a_deleted_face_would_be_noticed_at_all": sum(
            1 for r in rows if r["would_a_deleted_face_be_detected"]),
        "rows_where_a_deleted_face_is_invisible_to_its_own_gate": n_invisible,
        "rows_read_but_not_refused": n_not_refused,
        "rows_whose_gate_reads_a_path_it_cannot_fold": by_outcome[G_UNFOLDABLE],
        "rows_whose_gate_entry_is_unresolvable": by_outcome[G_NO_ENTRY],
        "by_outcome": {k: v for k, v in by_outcome.items() if v},
        "by_face_kind": {
            "machine_readable_face": {
                "rows": len(machine_faces),
                "refused": sum(1 for r in machine_faces if r["outcome"] == G_REFUSED),
                "invisible": sum(1 for r in machine_faces if r["outcome"] == G_INVISIBLE)},
            "rendered_face_a_human_reads": {
                "rows": len(render_faces),
                "refused": sum(1 for r in render_faces if r["outcome"] == G_REFUSED),
                "invisible": sum(1 for r in render_faces if r["outcome"] == G_INVISIBLE)},
        },
        "writers_whose_every_face_is_refused": sum(
            1 for w in by_writer.values() if w["every_face_refused"]),
        "writers_with_at_least_one_invisible_face": sum(
            1 for w in by_writer.values() if w["any_face_invisible"]),
        "gate_entry_depth": sorted({len(r["gate_entry"]["functions"]) for r in rows}),
        "machine_faces_a_gate_opens_that_E556_did_not_carry": gated_but_not_in_the_population,
        "runner_arms": runners,
        "runners_whose_process_exit_carries_a_failing_leg": sum(
            1 for x in runners if x.get("process_exit_carries_the_failure")),
        "control_arm": control,
    }

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "machine": MACHINE,
        "population_source": {
            "face": _rel(PARENT),
            "field": "rows[].gate_entry_points where kind == %s" % e557.N_CHAIN_GATE,
            "selector": "every gate leg E557 published over E556's message-only faces",
            "published": len(population()),
        },
        "rows": rows,
        "writers": [by_writer[k] for k in sorted(by_writer)],
        "summary": summary,
        "verdict": verdict,
        "verdict_line": (
            "%d of %d gated faces would be refused if they vanished and %d would not be "
            "noticed at all (%s); the %d machine-readable faces are refused %d/%d while "
            "the %d rendered faces a human reads are read by no gate at all (%d/%d)"
            % (n_refused, len(rows), n_invisible,
               ", ".join(r["face"] for r in rows if r["outcome"] in NOT_NOTICING_OUTCOMES)
               or "none",
               len(machine_faces), sum(1 for r in machine_faces if r["outcome"] == G_REFUSED),
               len(machine_faces), len(render_faces),
               sum(1 for r in render_faces if r["outcome"] == G_REFUSED), len(render_faces))),
        "method_note": (
            "The gate entry is followed statically from main() through the branch on the "
            "--check flag into every local function it calls; a guard inside a helper "
            "counts, and a load confined to the build path (outside that branch) does "
            "not.  A face is 'read' only when a load call's argument folds to the face "
            "path through the module's own constants, including Path(...).parents[N], and "
            "a write-mode open is never a read.  'Refused' means an explicit missing-file "
            "branch that returns non-zero or raises; an unguarded open is published as its "
            "own class because the leg still ends non-zero, but by a traceback rather than "
            "a refusal."),
        "disclosure": (
            "the gate opens %s beyond the faces E556 carried; those extra machine faces "
            "are refused by the same gate, so they are not part of this population and are "
            "published here only so the count is not read as 'no gate opens a JSON here'"
            % (", ".join(gated_but_not_in_the_population) or "nothing else")),
        "method_bound": (
            "static only: a path assembled from a run-time variable is published as "
            "unfoldable rather than guessed; a loader reached through a function in "
            "another module is not followed, so such a gate would read as 'never opens "
            "the face' -- the control arm is the guard against that being taken as proof "
            "(%s); 'would be noticed' is a statement about the leg's exit code, not about "
            "any human reading the receipt, and the runner arm is published separately "
            "because all three runners print the non-zero legs into a receipt."
            % CONTROL_GATE),
    }
    if write:
        os.makedirs(STATE_TILT, exist_ok=True)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
        _write(LATEST, face)
    return face


def _write(path, obj):
    raw = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(raw + "\n")


# ---------------------------------------------------------------- gate
def _rederive_rows(face):
    rows = face.get("rows") or []
    return {r.get("face") + "|" + r.get("writer") + "|" + str(r.get("gate_source")):
            r.get("outcome") for r in rows}


def face_problems(face):
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        return ["the population is empty"]

    by_outcome = {c: 0 for c in OUTCOME_VOCAB}
    for r in rows:
        if r.get("outcome") not in OUTCOME_VOCAB:
            probs.append("an outcome outside the vocabulary (%s)" % (r.get("outcome"),))
        by_outcome[r["outcome"]] += 1
        want = r["outcome"] in NOTICING_OUTCOMES
        if bool(r.get("would_a_deleted_face_be_detected")) != want:
            probs.append("a row's detection flag is not what its outcome says (%s)"
                         % (r.get("face"),))
        want_r = r["outcome"] in REFUSING_OUTCOMES
        if bool(r.get("would_a_deleted_face_be_refused")) != want_r:
            probs.append("a row's refusal flag is not what its outcome says (%s)"
                         % (r.get("face"),))
        # a class has to be backed by the evidence the class names
        if r["outcome"] == G_REFUSED:
            hits = [g for g in r["missing_file_guards"]
                    if g.get("about_the_gated_face") and g.get("exit") in REFUSING_EXITS]
            if not hits:
                probs.append("a row is called refused without a refusing guard (%s)"
                             % (r.get("face"),))
            if not [l for l in r["loads"] if l.get("path") == r["face"]]:
                probs.append("a row is called refused without ever opening the face (%s)"
                             % (r.get("face"),))
        if r["outcome"] == G_INVISIBLE:
            if [l for l in r["loads"] if l.get("path") == r["face"]]:
                probs.append("a row is called invisible and its own loads open the face (%s)"
                             % (r.get("face"),))
        if r["outcome"] == G_UNFOLDABLE:
            if not [l for l in r["loads"] if l.get("path") is None
                    and l.get("why") != "no_argument"]:
                probs.append("a row is called unfoldable with no unfoldable loader (%s)"
                             % (r.get("face"),))
        if r["outcome"] == G_NO_ENTRY:
            if r["gate_entry"].get("resolved"):
                probs.append("a row is called unresolvable and its entry resolved (%s)"
                             % (r.get("face"),))

    writer_rows = face.get("writers") or []
    for w in writer_rows:
        for f, cls in (w.get("outcomes") or {}).items():
            got = next((r["outcome"] for r in rows
                        if r["writer"] == w["writer"] and r["face"] == f), None)
            if got != cls:
                probs.append("the writer summary and the rows disagree on %s" % (f,))
        every = all(c == G_REFUSED for c in (w.get("outcomes") or {}).values())
        if bool(w.get("every_face_refused")) != every:
            probs.append("a writer's every-face-refused flag is not what its faces say (%s)"
                         % (w.get("writer"),))
        any_inv = any(c == G_INVISIBLE for c in (w.get("outcomes") or {}).values())
        if bool(w.get("any_face_invisible")) != any_inv:
            probs.append("a writer's any-invisible flag is not what its faces say (%s)"
                         % (w.get("writer"),))

    control = _control_arm()
    if not control["found"]:
        probs.append("the gate census is blind: %s" % control["why"])
    if s.get("control_arm") != control:
        probs.append("the published control arm is not the one the tree gives")

    runners = [runner_arm(c) for c in sorted({r["gate_source"] for r in rows})]
    expected = {
        "row_leg_pairs": len(rows),
        "distinct_gate_legs": len({(r["gate_source"], r["gate_leg"]) for r in rows}),
        "distinct_writers": len({r["writer"] for r in rows}),
        "rows_whose_gate_entry_could_be_followed": sum(
            1 for r in rows if r["gate_entry"].get("resolved")),
        "rows_a_deleted_face_would_be_refused": by_outcome[G_REFUSED],
        "rows_a_deleted_face_would_only_crash": by_outcome[G_CRASH],
        "rows_a_deleted_face_would_be_noticed_at_all": sum(
            1 for r in rows if r["would_a_deleted_face_be_detected"]),
        "rows_where_a_deleted_face_is_invisible_to_its_own_gate": by_outcome[G_INVISIBLE],
        "rows_read_but_not_refused": by_outcome[G_NOT_REFUSED],
        "rows_whose_gate_reads_a_path_it_cannot_fold": by_outcome[G_UNFOLDABLE],
        "rows_whose_gate_entry_is_unresolvable": by_outcome[G_NO_ENTRY],
        "by_outcome": {k: v for k, v in by_outcome.items() if v},
        "runner_arms": runners,
        "runners_whose_process_exit_carries_a_failing_leg": sum(
            1 for x in runners if x.get("process_exit_carries_the_failure")),
    }
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))

    if by_outcome[G_INVISIBLE]:
        want_v = V_INVISIBLE
    elif by_outcome[G_NOT_REFUSED]:
        want_v = V_NOT_REFUSED
    elif by_outcome[G_CRASH]:
        want_v = V_CRASH_ONLY
    else:
        want_v = V_REFUSED
    if face.get("verdict") != want_v:
        probs.append("the verdict is not what the rows derive (%r vs %r)"
                     % (face.get("verdict"), want_v))
    if not face.get("evidence_cutoff"):
        probs.append("the face carries no evidence_cutoff")
    if (face.get("population_source") or {}).get("published") != len(population()):
        probs.append("the parent face no longer publishes this many rows")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["face"], r["writer"], r["gate_source"]) for r in fresh["rows"]] != \
            [(r["face"], r["writer"], r["gate_source"]) for r in pub["rows"]]:
        problems.append("the published population is not the one E557 publishes now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the sources say now (%s)"
                                % (a["face"],))
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or []),
                      "refused": (pub.get("summary") or {}).get(
                          "rows_a_deleted_face_would_be_refused"),
                      "invisible": (pub.get("summary") or {}).get(
                          "rows_where_a_deleted_face_is_invisible_to_its_own_gate")},
                     ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    problems = [] if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else \
        ["two builds of the same sources differ"]
    if not problems:
        problems = list(face_problems(a))
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
_FIXTURE_HEAD = (
    "import argparse\n"
    "import json\n"
    "import os\n"
    "import sys\n"
    "from pathlib import Path\n"
    "ROOT = Path(__file__).resolve().parents[1]\n"
    "OUT_JSON = ROOT / 'results' / 'fx.json'\n"
    "OUT_MD = ROOT / 'research' / 'FX.md'\n"
)


def _fixture(main_body, extra=""):
    return (_FIXTURE_HEAD + extra + "\n"
            "def main(argv=None):\n"
            "    ap = argparse.ArgumentParser()\n"
            "    ap.add_argument('--check', action='store_true')\n"
            "    args = ap.parse_args(argv)\n"
            + main_body + "\n"
            "if __name__ == '__main__':\n"
            "    sys.exit(main())\n")


def selftest():
    fails = []
    n = 0

    def ok(label, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    def outcome(src, face="results/fx.json"):
        try:
            return measure_source(src, face)["outcome"]
        except Exception as exc:  # noqa: BLE001
            return "raised:%r" % (exc,)

    # 1) an explicit branch that returns non-zero is a refusal
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    if not OUT_JSON.exists():\n        print('missing')\n        return 1\n" \
        "    payload = json.loads(OUT_JSON.read_text(encoding='utf-8'))\n    return 0\n"
    ok("an explicit non-zero return is a refusal", outcome(src) == G_REFUSED)

    # 2) raise SystemExit is a refusal too (three of the writers spell it this way)
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    if not OUT_JSON.exists():\n        raise SystemExit('no face')\n" \
        "    return 0\n"
    ok("raise SystemExit is a refusal", outcome(src) == G_REFUSED)

    # 3) a missing-file branch that only prints is NOT a refusal
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    if not OUT_JSON.exists():\n        print('warn only')\n" \
        "    return 0\n"
    ok("a warning-only branch is not a refusal", outcome(src) == G_NOT_REFUSED)

    # 4) an unguarded open is its own class, not a refusal
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    payload = json.loads(OUT_JSON.read_text(encoding='utf-8'))\n" \
        "    return 0\n"
    ok("an unguarded open is published as a crash", outcome(src) == G_CRASH)

    # 5) a gate that opens a different path never touches this face
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    if not OUT_JSON.exists():\n        return 1\n    return 0\n"
    ok("the render the gate never opens is invisible", outcome(src, "research/FX.md") ==
       G_INVISIBLE)

    # 6) a write is not a read
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    OUT_MD.write_text('x', encoding='utf-8')\n    return 0\n"
    ok("writing the render does not count as reading it",
       outcome(src, "research/FX.md") == G_INVISIBLE)

    # 7) a guard inside a helper the gate calls counts (the flag reaches it)
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    return _guard(json.loads(OUT_JSON.read_text(encoding='utf-8')))\n" \
        "\ndef _guard(payload):\n    return 0\n"
    ok("helper reached from the flag branch counts as a read",
       outcome(src) in (G_CRASH,))

    # 8) a load confined to the build path is NOT a gate read
    src = _fixture("    if args.check:\n        return check()\n"
                   "    return build()\n") + \
        "\ndef check():\n    return 0\n" \
        "\ndef build():\n    return json.loads(OUT_JSON.read_text(encoding='utf-8'))\n"
    ok("a load outside the flag branch is not a gate read", outcome(src) == G_INVISIBLE)

    # 9) except FileNotFoundError that returns non-zero is a refusal
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    try:\n        payload = json.loads(OUT_JSON.read_text(encoding='utf-8'))\n" \
        "    except FileNotFoundError:\n        return 2\n    return 0\n"
    ok("an except that returns non-zero is a refusal", outcome(src) == G_REFUSED)

    # 10) except OSError that swallows is not
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    try:\n        payload = json.loads(OUT_JSON.read_text(encoding='utf-8'))\n" \
        "    except OSError:\n        pass\n    return 0\n"
    ok("an except that swallows is not a refusal", outcome(src) == G_NOT_REFUSED)

    # 11) the dest is honoured when argparse renames the flag
    src = (_FIXTURE_HEAD +
           "\ndef main(argv=None):\n    ap = argparse.ArgumentParser()\n"
           "    ap.add_argument('--check', dest='gate', action='store_true')\n"
           "    args = ap.parse_args(argv)\n    if args.gate:\n        return check()\n"
           "    return 0\n"
           "\ndef check():\n    if not OUT_JSON.exists():\n        return 1\n    return 0\n")
    ok("a renamed dest is followed", outcome(src) == G_REFUSED)

    # 12) main() that never branches on the flag is unresolvable, not invisible
    src = (_FIXTURE_HEAD +
           "\ndef main(argv=None):\n    import argparse as _a\n"
           "    return check()\n"
           "\ndef check():\n    if not OUT_JSON.exists():\n        return 1\n    return 0\n")
    ok("a main that never reads the flag is unresolvable", outcome(src) == G_NO_ENTRY)

    # 13) a path folded through a with-bound handle is read
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    with open(OUT_JSON, encoding='utf-8') as fh:\n" \
        "        payload = json.load(fh)\n    return 0\n"
    ok("a with-bound handle folds to the face", outcome(src) == G_CRASH)

    # 14) a path this scan cannot fold is unassessable, never silent
    src = _fixture("    if args.check:\n        return check('some/file.json')\n") + \
        "\ndef check(face):\n    return json.loads(open(face, encoding='utf-8').read())\n"
    ok("a run-time path is unassessable, not silent", outcome(src) == G_UNFOLDABLE)

    # 15) an open() with a write mode is not a read
    src = _fixture("    if args.check:\n        return check()\n") + \
        "\ndef check():\n    with open(OUT_JSON, 'w', encoding='utf-8') as fh:\n" \
        "        fh.write('x')\n    return 0\n"
    ok("a write-mode open is not a read", outcome(src) == G_INVISIBLE)

    # 16) the live control arm must be both arms at once
    ctl = _control_arm()
    ok("the live control arm separates refuse from invisible", ctl.get("found") is True)

    # 17) the live population is E557's, not a retyped list
    rows = population()
    ok("the population is five gate-leg rows over three writers",
       len(rows) == 5 and len(writers()) == 3)
    ok("the population's legs are three distinct chain legs", len(distinct_legs()) == 3)
    parent = json.load(io.open(PARENT, encoding="utf-8"))
    ok("every published row comes from E557's own gate entry points",
       {r["face"] for r in rows} <= {r.get("face") for r in parent.get("rows") or []})

    # 18) a hand-written verdict and a relabelled outcome are both refused
    face = build(write=False)
    ok("the live build has no problems", not face_problems(face))
    bad = json.loads(json.dumps(face))
    bad["verdict"] = "a_verdict_this_study_never_publishes"
    ok("a hand-written verdict is refused", bool(face_problems(bad)))
    bad = json.loads(json.dumps(face))
    for r in bad["rows"]:
        if r["outcome"] == G_REFUSED:
            r["outcome"] = G_INVISIBLE
            r["why"] = "relabelled"
            break
    ok("a refusal relabelled invisible is refused", any(
        "detection flag is not what its outcome says" in p or
        "invisible and its own loads open the face" in p for p in face_problems(bad)))
    bad = json.loads(json.dumps(face))
    for r in bad["rows"]:
        if r["outcome"] == G_INVISIBLE:
            r["outcome"] = G_REFUSED
            break
    ok("an invisible row relabelled refused is refused", any(
        "called refused without a refusing guard" in p for p in face_problems(bad)))
    bad = json.loads(json.dumps(face))
    bad["summary"]["rows_a_deleted_face_would_be_refused"] = 99
    ok("a count that does not re-derive is refused", any(
        "summary rows_a_deleted_face_would_be_refused" in p for p in face_problems(bad)))
    bad = json.loads(json.dumps(face))
    bad["summary"]["control_arm"]["found"] = False
    ok("a control arm that is not the tree's is refused", any(
        "control arm" in p for p in face_problems(bad)))
    bad = json.loads(json.dumps(face))
    bad.pop("evidence_cutoff", None)
    ok("a face with no cutoff is refused", any(
        "no evidence_cutoff" in p for p in face_problems(bad)))

    # 19) the runner arm reads the same three runners the legs live on
    arms = [runner_arm(c) for c in sorted({r["gate_source"] for r in rows})]
    ok("the runner arm is readable for every chain the legs live on",
       all(a.get("readable") for a in arms))
    ok("no runner's process exit carries a failing leg (measured, not assumed)",
       all(a.get("process_exit_carries_the_failure") is False for a in arms))

    print("e558 selftest %d/%d PASS" % (n - len(fails), n))
    for f in fails:
        print("FAIL: %s" % f)
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"rows": len(face["rows"]), "verdict": face["verdict"],
                          "verdict_line": face["verdict_line"]}, ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "population":
        print(json.dumps({"rows": population(), "legs": distinct_legs()},
                         ensure_ascii=False))
        return 0
    raise SystemExit("unknown command: %s (build|check|verify|selftest|population)" % cmd)


if __name__ == "__main__":
    sys.exit(main())