"""E554 -- the repository's whole ``wrote <path>`` render population, split by two facts.

E553 (r1579) measured six ``etf_phase_*`` render sites and found that nothing in
the repository reads any of them back.  Those six were the parent face's own
rows, not the repository's render population.  This study discovers the
population from the render call itself -- every ``print("wrote", ...)`` (and the
short aliases ``p``/``log``) whose statically readable first word is ``wrote`` --
and asks the two questions E553 showed decide whether a rendered path is ever a
machine-visible announcement:

  * **can the writer run at all in this repository?**  A source that spawns the
    script and captures its stdout can see the line; a spawn that leaves stdout
    on the console cannot be parsed by the spawner; a writer no source spawns is
    only ever run by a human typing it.
  * **does the face the message names have another announcement?**  A canonical
    ``<stem>_latest.json`` pointer, or a source literal naming the path, means a
    machine can find the face without the message.  If neither exists, the face
    is announced only by the message.

A third arm keeps studies that write and later re-read their own face out of the
at-risk class, with their own count (the card asks for that explicitly).

What the message names is not always a path: some sites render a count
(``print("wrote", len(lines))``) or a dict key (``face['_written']``), and a
resolved name may point at a constant this scan cannot fold.  Those rows are
published as ``unassessable`` with the reason, never folded into ``only_message``
(unassessable != unannounced).

    python scripts/e554_wrote_population.py build      # publish the face
    python scripts/e554_wrote_population.py check      # re-derive from source; problems must be []
    python scripts/e554_wrote_population.py verify     # two builds identical
    python scripts/e554_wrote_population.py selftest    # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "wrotepopulation_latest.json")
DATED_PREFIX = "WROTEPOPULATION"

STUDY = "E554"
CARD = "E554"
TITLE = ("the repository's whole wrote-path render population, split by spawnability "
         "and by what else announces the face")
EVIDENCE_CUTOFF = "2026-11-08"

MESSAGE_WORD = "wrote"
RENDER_FUNCS = ("print", "p", "log")

# ---- can the writer run ---------------------------------------------------
S_CAPTURED = "spawned_by_a_source_that_captures_its_stdout"
S_UNCAPTURED = "spawned_by_a_source_that_leaves_stdout_on_the_console"
S_NONE = "no_source_in_the_repository_spawns_this_writer"
SPAWN_VOCAB = (S_CAPTURED, S_UNCAPTURED, S_NONE)

# ---- what else announces the face -----------------------------------------
A_ONLY_MESSAGE = "only_the_rendered_message_announces_this_face"
A_SOURCE_LITERAL = "a_source_literal_announces_this_face"
A_POINTER_FACE = "a_pointer_face_announces_this_face"
A_BOTH = "both_a_source_literal_and_a_pointer_face_announce_this_face"
A_UNASSESSABLE = "the_message_names_no_face_this_scan_can_resolve"
ANNOUNCE_VOCAB = (A_ONLY_MESSAGE, A_SOURCE_LITERAL, A_POINTER_FACE, A_BOTH, A_UNASSESSABLE)

# ---- what the writer is ---------------------------------------------------
W_LANE_SCRIPT = "a_script_under_scripts_that_a_lane_could_run"
W_SCRATCH = "a_scratch_script_under_the_root_or_results"
W_OTHER = "a_python_source_somewhere_else_in_the_tree"
WORKSPACE_VOCAB = (W_LANE_SCRIPT, W_SCRATCH, W_OTHER)

# ---- why the message names no resolvable face -----------------------------
U_NO_SECOND_ARGUMENT = "the_message_names_nothing_besides_the_word"
U_NOT_A_PATH_VALUE = "the_second_argument_is_a_count_or_a_flag_not_a_path"
U_RUNTIME_VALUE = "the_second_argument_is_computed_at_run_time"
U_SUBSCRIPT = "the_second_argument_is_a_key_of_a_dict_built_at_run_time"
U_UNFOLDABLE_NAME = "the_second_argument_is_a_name_this_scan_cannot_fold"
UNRESOLVED_VOCAB = (U_NO_SECOND_ARGUMENT, U_NOT_A_PATH_VALUE, U_RUNTIME_VALUE,
                    U_SUBSCRIPT, U_UNFOLDABLE_NAME)

# ---- risk classes ---------------------------------------------------------
R_MESSAGE_ONLY_RUNNABLE = "message_only_and_a_source_can_spawn_the_writer"
R_MESSAGE_ONLY_UNRUNNABLE = "message_only_and_no_source_can_spawn_the_writer"
R_ANNOUNCED_ELSEWHERE = "the_face_is_announced_without_the_message"
R_SELF_ANNOUNCING = "the_writer_itself_reads_the_face_back"
R_UNASSESSABLE = "the_message_names_no_resolvable_face"
RISK_VOCAB = (R_MESSAGE_ONLY_RUNNABLE, R_MESSAGE_ONLY_UNRUNNABLE, R_ANNOUNCED_ELSEWHERE,
              R_SELF_ANNOUNCING, R_UNASSESSABLE)
AT_RISK_CLASSES = (R_MESSAGE_ONLY_RUNNABLE, R_MESSAGE_ONLY_UNRUNNABLE)

V_SOME_AT_RISK = ("some_wrote_messages_are_the_only_announcement_of_a_face_that_nothing_"
                  "else_names")
V_NONE_AT_RISK = "every_resolvable_wrote_message_has_an_announcement_that_survives_its_loss"

SPAWN_FUNCS = ("run", "call", "check_call", "check_output", "Popen", "system",
               "spawn", "spawnv", "spawnl", "popen")

SKIP_DIRS = {".git", "data", "__pycache__", "media", "_quarantine",
             "node_modules", ".codely-cli"}
SELF_EXCLUDE = re.compile(r"(^|/)e55[0-9]_|results/state_tilt/[A-Z]*WROTEPOPULATION"
                          r"|results/state_tilt/wrotepopulation_latest")

_PATHish = re.compile(r"^(results|docs|data|state|research|knowledge|logs)/")


# ---------------------------------------------------------------- reads
def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


_WALK = {}
_CORPUS = None
_TOKENS = None
_POINTERS = None


def _walk_sources(exts=(".py",)):
    exts = tuple(exts)
    if exts in _WALK:
        return _WALK[exts]
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(exts):
                continue
            p = os.path.join(base, fn)
            rel = _rel(p)
            if SELF_EXCLUDE.search(rel):
                continue
            out.append((rel, p))
    _WALK[exts] = sorted(out)
    return _WALK[exts]


def _corpus():
    """Every text source, read exactly once (E442 family: one pass shared)."""
    global _CORPUS
    if _CORPUS is not None:
        return _CORPUS
    corpus = {}
    for rel, path in _walk_sources((".py", ".ps1", ".bat", ".cmd", ".sh")):
        try:
            if os.path.getsize(path) > 4 * 1024 * 1024:
                continue
            corpus[rel] = _read(path)
        except OSError:
            continue
    _CORPUS = corpus
    return _CORPUS


def _token_index():
    """file -> set of word tokens, so a spawn search never scans 2400 texts per site."""
    global _TOKENS
    if _TOKENS is not None:
        return _TOKENS
    idx = {}
    for rel, text in _corpus().items():
        idx[rel] = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", text))
    _TOKENS = idx
    return _TOKENS


def _pointer_faces():
    global _POINTERS
    if _POINTERS is not None:
        return _POINTERS
    out = {}
    for rel, path in _walk_sources((".json",)):
        if not os.path.basename(rel).endswith("_latest.json"):
            continue
        try:
            if os.path.getsize(path) > 512 * 1024:
                continue
            out[rel] = _read(path)
        except OSError:
            continue
    _POINTERS = out
    return _POINTERS


# ---------------------------------------------------------------- the population
def _word_of_render(call):
    """The first word of the message, from the call's own first argument."""
    if not call.args:
        return None
    first = call.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        parts = first.value.split()
        return parts[0] if parts else None
    if isinstance(first, ast.BinOp) and isinstance(first.op, ast.Mod):
        fmt = first.left
        if isinstance(fmt, ast.Constant) and isinstance(fmt.value, str):
            parts = fmt.value.split()
            return parts[0] if parts else None
    return None


def _render_call(tree, line):
    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or node.lineno != line:
            continue
        try:
            fname = ast.unparse(node.func)
        except Exception:
            continue
        if fname not in RENDER_FUNCS:
            continue
        if _word_of_render(node) == MESSAGE_WORD:
            best = node
    return best


JOIN_LEAVES = ("join",)
IDENTITY_LEAVES = ("relpath", "abspath", "resolve", "str", "Path", "PurePath",
                   "as_posix", "replace", "relative_to", "_rel", "_relpath",
                   "_relative", "normpath")
DIRNAME_LEAVES = ("dirname",)
# A *method* wrapper (``p.replace("\\", "/")``) folds through its receiver; a
# module-qualified function (``os.path.abspath(__file__)``) folds through its
# argument.  Reading the receiver for both silently unfolds every ROOT constant.
METHOD_LEAVES = ("replace", "resolve", "as_posix", "relative_to", "with_suffix",
                 "absolute", "expanduser")
# ``__file__`` folds to the root marker: the site reports repo-relative faces, and
# ``dirname(dirname(abspath(__file__)))`` is exactly the root, so the marker keeps
# ``ROOT / "results" / "x.json"`` folding to ``results/x.json``.
ROOT_MARKERS = {"__file__", "__file_path__", "HERE", "FILE"}
# A message that renders a count (``len(lines)``) names no path at all -- its own
# reason, not "a value computed at run time".
COUNT_LEAVES = ("len", "sum", "int", "float", "bool", "round", "abs")


def _leaf(func):
    try:
        name = ast.unparse(func)
    except Exception:
        return ""
    return name.split(".")[-1]


def _norm(v):
    v = v.replace("\\", "/")
    while v.startswith("./"):
        v = v[2:]
    return v


def _fold(expr, consts, depth=0):
    """Fold a path expression to a repo-relative string, or say why not.

    The tree names its output faces in four spellings that all mean one thing:
    a string constant, ``os.path.join(<const>, "x.json")``, ``ROOT / "results" /
    "x.json"`` and a *presentation wrapper* around any of them (``os.path.relpath``,
    ``.replace("\\\\", "/")``, ``path.relative_to(ROOT)``, a local ``_rel``).  A
    fold that stops at the wrapper publishes 112 unresolvable messages for a
    question about face announcements, so the wrappers are folded through.
    """
    if depth > 8 or expr is None:
        return None, None
    if isinstance(expr, ast.Constant):
        if isinstance(expr.value, str):
            return _norm(expr.value), None
        return None, U_NOT_A_PATH_VALUE
    if isinstance(expr, ast.Name):
        if expr.id in consts:
            return consts[expr.id], None
        if expr.id in ROOT_MARKERS:
            return "", None
        return None, U_UNFOLDABLE_NAME
    if isinstance(expr, ast.Subscript):
        if isinstance(expr.value, ast.Name) and isinstance(expr.slice, ast.Constant):
            key = "__sub__%s:%s" % (expr.value.id, expr.slice.value)
            if key in consts:
                return consts[key], None
        return None, U_SUBSCRIPT
    if isinstance(expr, ast.BinOp):
        if isinstance(expr.op, (ast.Div, ast.Add)):
            left, why = _fold(expr.left, consts, depth + 1)
            right, why2 = _fold(expr.right, consts, depth + 1)
            if left is None:
                return None, why
            if right is None:
                return None, why2
            if isinstance(expr.op, ast.Add):
                return left + right, None
            return _norm(os.path.join(left, right)), None
        if isinstance(expr.op, ast.Mod):
            cands = expr.right.elts if isinstance(expr.right, ast.Tuple) else [expr.right]
            for c in cands:
                val, why = _fold(c, consts, depth + 1)
                if val is not None and _PATHish.match(val):
                    return val, None
            return None, U_RUNTIME_VALUE
        return None, U_RUNTIME_VALUE
    if isinstance(expr, ast.Call):
        leaf = _leaf(expr.func)
        if leaf == "join":
            parts = []
            for a in expr.args:
                val, why = _fold(a, consts, depth + 1)
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
        if leaf in DIRNAME_LEAVES:
            base, why = _fold(expr.args[0] if expr.args else None, consts, depth + 1)
            if base is None:
                return None, why
            return _norm(os.path.dirname(base)), None
        if leaf in IDENTITY_LEAVES:
            if isinstance(expr.func, ast.Attribute) and leaf in METHOD_LEAVES:
                target = expr.func.value
            else:
                target = expr.args[0] if expr.args else None
            return _fold(target, consts, depth + 1)
        if leaf in COUNT_LEAVES:
            return None, U_NOT_A_PATH_VALUE
        return None, U_RUNTIME_VALUE
    if isinstance(expr, ast.Attribute):
        return _fold(expr.value, consts, depth + 1)
    return None, U_RUNTIME_VALUE


def _module_constants(tree):
    """Module-level ``NAME = <path expression>``, folded in declaration order."""
    raw = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name):
            raw.append((node.targets[0].id, node.value))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.value is not None:
            raw.append((node.target.id, node.value))
    consts = {}
    for name, value in raw:
        val, _why = _fold(value, consts)
        if val is not None:
            consts[name] = val
    return consts


def _local_scope(tree, render_line, consts):
    """Names assigned before the render line inside the enclosing function.

    A site that writes to a variable first (``p = ROOT / "results" / "x.json"``)
    names a face as plainly as a module constant does; a fold that only reads
    module scope publishes those as unfoldable.
    """
    func = _enclosing_function(tree, render_line)
    scope = {}
    assignments = []
    for node in ast.walk(func if func is not None else tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name) and node.lineno < render_line:
            assignments.append((node.lineno, node.targets[0].id, node.value))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and \
                node.value is not None and node.lineno < render_line:
            assignments.append((node.lineno, node.target.id, node.value))
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Subscript) and node.lineno < render_line:
            tgt = node.targets[0]
            if isinstance(tgt.value, ast.Name) and isinstance(tgt.slice, ast.Constant):
                assignments.append((node.lineno,
                                    "__sub__%s:%s" % (tgt.value.id, tgt.slice.value),
                                    node.value))
    merged = dict(consts)
    for _line, name, value in sorted(assignments, key=lambda a: a[0]):
        val, _why = _fold(value, merged)
        if val is not None:
            # Nothing is dropped here: a name whose own value does not fold still
            # carries the module-level meaning down the chain, and popping it
            # cascaded through every constant defined in terms of it (a first
            # draft published 71 unfoldable names for this reason).
            merged[name] = val
            scope[name] = val
    return merged


def _resolve_face(call, consts, tree=None):
    """(face_rel_or_None, resolution_class_or_None, reason_or_None)."""
    scope = _local_scope(tree, call.lineno, consts) if tree is not None else consts
    if len(call.args) < 2:
        first = call.args[0] if call.args else None
        if isinstance(first, ast.BinOp) and isinstance(first.op, ast.Mod):
            cands = first.right.elts if isinstance(first.right, ast.Tuple) else [first.right]
            why = None
            for c in cands:
                val, w = _fold(c, scope)
                if val is not None and _PATHish.match(val):
                    return val, "resolved_from_the_format_middle", None
                why = why or w
            return None, None, why or U_RUNTIME_VALUE
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            # ``print("wrote results/x.json")`` -- the message spells the path in
            # its own text; that is still a machine-visible name of the face.
            for tok in first.value.split():
                tok = _norm(tok.strip(".,;:()[]"))
                if _PATHish.match(tok):
                    return tok, "resolved_from_the_message_text", None
        return None, None, U_NO_SECOND_ARGUMENT

    arg = call.args[1]
    val, why = _fold(arg, scope)
    if val is not None and _PATHish.match(val):
        cls = "resolved_literal" if isinstance(arg, ast.Constant) else \
            ("resolved_module_constant" if isinstance(arg, ast.Name) and arg.id in consts
             else "resolved_computed_path")
        return val, cls, None
    if val is not None:
        return None, None, U_NOT_A_PATH_VALUE
    return None, None, why


def _workspace_class(writer_rel):
    if writer_rel.startswith("scripts/"):
        return W_LANE_SCRIPT
    base = os.path.basename(writer_rel)
    if writer_rel.startswith("results/") or base.startswith(("_r", "_w", "_tmp", "_e")):
        return W_SCRATCH
    return W_OTHER


def _enclosing_function(tree, line):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best


def _main_guard_calls(tree):
    called = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        try:
            cond = ast.unparse(node.test)
        except Exception:
            cond = ""
        if "__name__" not in cond:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                try:
                    called.add(ast.unparse(inner.func))
                except Exception:
                    pass
    return called


def _reachable_from_guard(tree, func):
    if func is None:
        return False
    guard = _main_guard_calls(tree)
    if func.name in guard:
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in guard:
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    try:
                        if ast.unparse(inner.func) == func.name:
                            return True
                    except Exception:
                        pass
    return False


def _self_reread(tree, writer_rel, consts, face_rel):
    """Does the writer itself read the face back (the self-announcing arm)?"""
    names = {n for n, v in consts.items() if v and v == face_rel}
    if not names and face_rel:
        base = os.path.basename(face_rel)
        # ``face_rel.endswith(v)`` with an empty or one-segment ``v`` (a folded
        # ROOT is ``""`` here) matched every constant in the module and published
        # 29 "self re-read" rows for writers that only name their output root.
        names = {n for n, v in consts.items()
                 if v and len(v) >= len(base) and v.endswith(base)}
    if not names:
        return []
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        try:
            fname = ast.unparse(node.func)
        except Exception:
            continue
        if not (fname.endswith("open") or fname.endswith("load") or
                fname.endswith("read_text") or fname.endswith("loads")):
            continue
        # An ``open(OUT, "w")`` two lines above the message is the write, not a
        # re-read: without this the write path counted as the writer announcing
        # its own face (a first draft published 29 "self re-read" rows this way).
        mode = ""
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            mode = str(node.args[1].value)
        for k in node.keywords:
            if k.arg == "mode" and isinstance(k.value, ast.Constant):
                mode = str(k.value.value)
        if any(ch in mode for ch in "wax+"):
            continue
        try:
            argtext = " ".join(ast.unparse(a) for a in node.args)
        except Exception:
            argtext = ""
        for n in names:
            if re.search(r"\b%s\b" % re.escape(n), argtext):
                hits.append({"line": node.lineno, "call": fname, "constant": n})
                break
    return hits


def _spawners_of(script_rel, module_name):
    out = []
    stems = (os.path.basename(script_rel), module_name)
    tokens = _token_index()
    for rel, text in sorted(_corpus().items()):
        tok = tokens.get(rel) or set()
        if not any(s in tok or s in text for s in stems):
            continue
        if rel == script_rel:
            continue
        if rel.endswith(".py"):
            for line, captured in _spawn_lines(rel, text, stems):
                out.append({"source": rel, "line": line, "construct": "spawn",
                            "captures": captured})
        else:
            for i, line in enumerate(text.splitlines(), 1):
                if not any(s in line for s in stems):
                    continue
                if not re.search(r"\b(python|pythonw|py|pwsh|powershell|cmd|Start-Process|"
                                 r"schtasks|-File)\b", line):
                    continue
                captured = bool(re.search(r"\|\s*Out-String|=\s*&|\(&|\$\(|\bSelect-String\b",
                                          line))
                out.append({"source": rel, "line": i, "construct": "shell_spawn",
                            "captures": captured})
    return out


def _spawn_lines(rel, text, stems):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        try:
            fname = ast.unparse(node.func)
        except Exception:
            continue
        leaf = fname.split(".")[-1]
        if leaf not in SPAWN_FUNCS:
            continue
        try:
            argtext = " ".join(ast.unparse(a) for a in node.args)
        except Exception:
            argtext = ""
        kw = " ".join("%s=%s" % (k.arg, ast.unparse(k.value)) for k in node.keywords if k.arg)
        if not any(s in argtext or s in kw for s in stems):
            continue
        captured = ("capture_output" in kw and "True" in kw) or \
                   (re.search(r"stdout\s*=\s*(subprocess\.)?PIPE", kw) is not None) or \
                   leaf == "check_output"
        lines.append((node.lineno, bool(captured)))
    return lines


_ANNOUNCE_CACHE = {}


def _announcements_of(face_rel, writer_rel):
    key = (face_rel, writer_rel)
    if key in _ANNOUNCE_CACHE:
        return _ANNOUNCE_CACHE[key]
    found = []
    base = os.path.basename(face_rel)
    stem = base.rsplit(".", 1)[0]
    for rel, text in sorted(_corpus().items()):
        if rel == writer_rel:
            continue
        if face_rel in text or base in text:
            found.append({"source": rel, "kind": "source_literal"})
    for rel, text in sorted(_pointer_faces().items()):
        if os.path.basename(rel) == "%s_latest.json" % stem or face_rel in text or base in text:
            found.append({"source": rel, "kind": "pointer"})
    _ANNOUNCE_CACHE[key] = found
    return found


# ---------------------------------------------------------------- classification
def classify_spawn(spawners):
    if any(s["captures"] for s in spawners):
        return S_CAPTURED
    if spawners:
        return S_UNCAPTURED
    return S_NONE


def classify_announce(face_rel, announcements):
    if not face_rel:
        return A_UNASSESSABLE
    literal = any(a["kind"] == "source_literal" for a in announcements)
    pointer = any(a["kind"] == "pointer" for a in announcements)
    if literal and pointer:
        return A_BOTH
    if literal:
        return A_SOURCE_LITERAL
    if pointer:
        return A_POINTER_FACE
    return A_ONLY_MESSAGE


def classify_risk(spawn_cls, ann_cls, self_reread):
    if ann_cls == A_UNASSESSABLE:
        return R_UNASSESSABLE
    if self_reread:
        return R_SELF_ANNOUNCING
    if ann_cls == A_ONLY_MESSAGE:
        return R_MESSAGE_ONLY_UNRUNNABLE if spawn_cls == S_NONE else R_MESSAGE_ONLY_RUNNABLE
    return R_ANNOUNCED_ELSEWHERE


def _rederive_spawn(row):
    return classify_spawn(row["facts"]["spawners"])


def _rederive_announce(row):
    return classify_announce(row["face"]["path"], row["facts"]["announcements"])


def _rederive_risk(row):
    return classify_risk(row["spawn_class"], row["announcement_class"],
                         bool(row["facts"]["self_reread"]))


def population():
    """Every render call in the tree whose statically readable first word is 'wrote'."""
    rows = []
    for rel, path in _walk_sources((".py",)):
        try:
            if os.path.getsize(path) > 4 * 1024 * 1024:
                continue
            text = _read(path)
            tree = ast.parse(text)
        except (OSError, SyntaxError):
            continue
        consts = _module_constants(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            try:
                fname = ast.unparse(node.func)
            except Exception:
                continue
            if fname not in RENDER_FUNCS:
                continue
            if _word_of_render(node) != MESSAGE_WORD:
                continue
            rows.append({"writer": rel, "line": node.lineno, "tree": tree,
                         "call": node, "consts": consts})
    rows.sort(key=lambda r: (r["writer"], r["line"]))
    return rows


def build(write=True):
    published = []
    for row in population():
        tree = row["tree"]
        call = row["call"]
        face_rel, face_res, reason = _resolve_face(call, row["consts"], tree)
        module_name = os.path.basename(row["writer"]).rsplit(".", 1)[0]
        spawners = _spawners_of(row["writer"], module_name)
        announcements = _announcements_of(face_rel, row["writer"]) if face_rel else []
        reread = _self_reread(tree, row["writer"],
                              _local_scope(tree, row["line"], row["consts"]), face_rel)
        spawn_cls = classify_spawn(spawners)
        ann_cls = classify_announce(face_rel, announcements)
        risk = classify_risk(spawn_cls, ann_cls, bool(reread))
        func = _enclosing_function(tree, row["line"])
        try:
            render_text = " ".join(ast.unparse(call).split())[:200]
        except Exception:
            render_text = ""
        published.append({
            "writer": row["writer"],
            "line": row["line"],
            "workspace_class": _workspace_class(row["writer"]),
            "render": {
                "text": render_text,
                "enclosing_function": func.name if func is not None else None,
                "reachable_from_the_main_guard": _reachable_from_guard(tree, func),
            },
            "face": {"path": face_rel, "resolution": face_res, "unresolved_because": reason},
            "facts": {
                "spawners": spawners,
                "announcements": announcements,
                "self_reread": reread,
            },
            "spawn_class": spawn_cls,
            "announcement_class": ann_cls,
            "risk_class": risk,
        })

    by_spawn = {c: 0 for c in SPAWN_VOCAB}
    by_announce = {c: 0 for c in ANNOUNCE_VOCAB}
    by_risk = {c: 0 for c in RISK_VOCAB}
    by_workspace = {c: 0 for c in WORKSPACE_VOCAB}
    by_unresolved = {c: 0 for c in UNRESOLVED_VOCAB}
    cross = {}
    for r in published:
        by_spawn[r["spawn_class"]] += 1
        by_announce[r["announcement_class"]] += 1
        by_risk[r["risk_class"]] += 1
        by_workspace[r["workspace_class"]] += 1
        if r["face"]["unresolved_because"]:
            by_unresolved[r["face"]["unresolved_because"]] += 1
        key = "%s|%s" % (r["spawn_class"], r["announcement_class"])
        cross[key] = cross.get(key, 0) + 1

    at_risk = by_risk[R_MESSAGE_ONLY_RUNNABLE] + by_risk[R_MESSAGE_ONLY_UNRUNNABLE]
    distinct_faces = sorted({r["face"]["path"] for r in published if r["face"]["path"]})
    summary = {
        "rows": len(published),
        "distinct_writers": len({r["writer"] for r in published}),
        "distinct_resolved_faces": len(distinct_faces),
        "by_spawn_class": by_spawn,
        "by_announcement_class": by_announce,
        "by_risk_class": by_risk,
        "by_workspace_class": by_workspace,
        "by_unresolved_reason": by_unresolved,
        "cross_tab_spawn_x_announce": cross,
        "resolvable_faces": len(published) - by_announce[A_UNASSESSABLE],
        "writers_spawned_by_any_source": len(published) - by_spawn[S_NONE],
        "writers_spawned_by_a_capturing_source": by_spawn[S_CAPTURED],
        "message_only_faces_whose_writer_is_spawnable": by_risk[R_MESSAGE_ONLY_RUNNABLE],
        "message_only_faces_whose_writer_nobody_can_spawn": by_risk[R_MESSAGE_ONLY_UNRUNNABLE],
        "at_risk_rows": at_risk,
        "self_announcing_rows": by_risk[R_SELF_ANNOUNCING],
        "unassessable_rows": by_risk[R_UNASSESSABLE],
        "lane_scripts_in_the_population": by_workspace[W_LANE_SCRIPT],
        "scratch_scripts_in_the_population": by_workspace[W_SCRATCH],
    }
    verdict = V_SOME_AT_RISK if at_risk else V_NONE_AT_RISK
    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "method": "AST discovery over every .py source; a render call whose first "
                      "argument's statically readable first word is 'wrote'",
            "render_functions": list(RENDER_FUNCS),
        },
        "rows": published,
        "summary": summary,
        "verdict": verdict,
        "verdict_line": verdict,
        "method_note": (
            "a spawn that does not capture stdout cannot be parsed by the spawner; a "
            "writer no source spawns is only run by a human; an unresolved message names "
            "no face this scan can see (published as unassessable, never as unannounced)"),
        "method_bound": (
            "spawn detection is static: a source that names the script inside a spawn "
            "function's arguments or a shell command line, nothing follows an alias or a "
            "variable-built path; announcement detection reads literals in sources and "
            "small *_latest.json pointer faces only"),
    }
    if write:
        dated = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
        blob = json.dumps(face, ensure_ascii=False, indent=1)
        io.open(dated, "w", encoding="utf-8", newline="\n").write(blob + "\n")
        io.open(LATEST, "w", encoding="utf-8", newline="\n").write(blob + "\n")
        print(json.dumps({"rows": len(published),
                          "at_risk": at_risk,
                          "spawnable_message_only": by_risk[R_MESSAGE_ONLY_RUNNABLE],
                          "unrunnable_message_only": by_risk[R_MESSAGE_ONLY_UNRUNNABLE],
                          "unassessable": by_risk[R_UNASSESSABLE],
                          "verdict": verdict,
                          "wrote": os.path.relpath(dated, ROOT).replace("\\", "/")},
                         ensure_ascii=False))
    return face


# ---------------------------------------------------------------- gates
def face_problems(face):
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        probs.append("the population is empty")
        return probs

    by_spawn = {c: 0 for c in SPAWN_VOCAB}
    by_announce = {c: 0 for c in ANNOUNCE_VOCAB}
    by_risk = {c: 0 for c in RISK_VOCAB}
    by_workspace = {c: 0 for c in WORKSPACE_VOCAB}
    cross = {}
    for r in rows:
        sp, an, rk = r.get("spawn_class"), r.get("announcement_class"), r.get("risk_class")
        for val, vocab, bucket, name in ((sp, SPAWN_VOCAB, by_spawn, "spawn"),
                                         (an, ANNOUNCE_VOCAB, by_announce, "announcement"),
                                         (rk, RISK_VOCAB, by_risk, "risk")):
            if val not in vocab:
                probs.append("a %s class outside the vocabulary: %s" % (name, val))
            else:
                bucket[val] += 1
        ws = r.get("workspace_class")
        if ws not in WORKSPACE_VOCAB:
            probs.append("a workspace class outside the vocabulary: %s" % (ws,))
        else:
            by_workspace[ws] += 1
        cross["%s|%s" % (sp, an)] = cross.get("%s|%s" % (sp, an), 0) + 1
        if sp in SPAWN_VOCAB and sp != _rederive_spawn(r):
            probs.append("a row's spawn class is not what its own facts say (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if an in ANNOUNCE_VOCAB and an != _rederive_announce(r):
            probs.append("a row's announcement class is not what its own facts say (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if rk in RISK_VOCAB and rk != _rederive_risk(r):
            probs.append("a row's risk class is not what its classes say (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        facts = r.get("facts") or {}
        if sp == S_CAPTURED and not any(x.get("captures") for x in facts.get("spawners") or []):
            probs.append("a row is called captured with no capturing spawner (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if sp == S_NONE and facts.get("spawners"):
            probs.append("a row is called unspawnable while it lists spawners (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if an == A_ONLY_MESSAGE and not r["face"].get("path"):
            probs.append("a message-only row resolves no face (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if an == A_ONLY_MESSAGE and [a for a in facts.get("announcements") or []
                                     if a.get("kind") in ("source_literal", "pointer")]:
            probs.append("a message-only row lists an announcement (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if an == A_UNASSESSABLE and r["face"].get("path"):
            probs.append("an unassessable row resolves a face (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if an != A_UNASSESSABLE and not r["face"].get("resolution"):
            probs.append("a resolved row publishes no resolution class (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if an == A_UNASSESSABLE and r["face"].get("unresolved_because") not in UNRESOLVED_VOCAB:
            probs.append("an unassessable row gives no vocabulary reason (%s:%s)"
                         % (r.get("writer"), r.get("line")))
        if rk == R_SELF_ANNOUNCING and not facts.get("self_reread"):
            probs.append("a self-announcing row lists no re-read (%s:%s)"
                         % (r.get("writer"), r.get("line")))

    expected = {
        "rows": len(rows),
        "distinct_writers": len({r["writer"] for r in rows}),
        "distinct_resolved_faces": len({r["face"]["path"] for r in rows if r["face"].get("path")}),
        "by_spawn_class": by_spawn,
        "by_announcement_class": by_announce,
        "by_risk_class": by_risk,
        "by_workspace_class": by_workspace,
        "cross_tab_spawn_x_announce": cross,
        "resolvable_faces": len(rows) - by_announce[A_UNASSESSABLE],
        "writers_spawned_by_any_source": len(rows) - by_spawn[S_NONE],
        "writers_spawned_by_a_capturing_source": by_spawn[S_CAPTURED],
        "message_only_faces_whose_writer_is_spawnable": by_risk[R_MESSAGE_ONLY_RUNNABLE],
        "message_only_faces_whose_writer_nobody_can_spawn": by_risk[R_MESSAGE_ONLY_UNRUNNABLE],
        "at_risk_rows": by_risk[R_MESSAGE_ONLY_RUNNABLE] + by_risk[R_MESSAGE_ONLY_UNRUNNABLE],
        "self_announcing_rows": by_risk[R_SELF_ANNOUNCING],
        "unassessable_rows": by_risk[R_UNASSESSABLE],
        "lane_scripts_in_the_population": by_workspace[W_LANE_SCRIPT],
        "scratch_scripts_in_the_population": by_workspace[W_SCRATCH],
    }
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))
    want = V_SOME_AT_RISK if expected["at_risk_rows"] else V_NONE_AT_RISK
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)" % (face.get("verdict"), want))
    if not face.get("evidence_cutoff"):
        probs.append("the face carries no evidence_cutoff")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["writer"], r["line"]) for r in fresh["rows"]] != \
            [(r["writer"], r["line"]) for r in pub["rows"]]:
        problems.append("the published population is not the one the sources have now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the sources say now (%s:%s)"
                                % (a["writer"], a["line"]))
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or []),
                      "at_risk": (pub.get("summary") or {}).get("at_risk_rows")},
                     ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    problems = [] if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else \
        ["two builds of the same sources differ"]
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []
    n = 0

    def ok(name, cond, detail=""):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name + ((" -- " + detail) if detail else ""))
        print(("PASS " if cond else "FAIL ") + name + ((" -- " + detail) if detail else ""))

    # --- word extraction
    def word(src):
        tree = ast.parse(textwrap.dedent(src))
        call = [x for x in ast.walk(tree) if isinstance(x, ast.Call)][0]
        return _word_of_render(call)

    ok("word: a constant first argument gives its first word",
       word('print("wrote", OUT)') == "wrote", str(word('print("wrote", OUT)')))
    ok("word: a %-formatted message gives the format string's first word",
       word('print("wrote %s" % OUT)') == "wrote")
    ok("word: leading spaces are dropped", word('print("  wrote", p)') == "wrote")
    ok("word: a call with no constant first argument has no word",
       word("print(name, OUT)") is None)
    ok("word: an f-string has no statically known word", word('print(f"wrote {OUT}")') is None)

    # --- face resolution
    def resolve(src):
        tree = ast.parse(textwrap.dedent(src))
        consts = _module_constants(tree)
        call = [x for x in ast.walk(tree) if isinstance(x, ast.Call)
                and _leaf(x.func) in RENDER_FUNCS][0]
        return _resolve_face(call, consts, tree)

    ok("face: a module-level constant string is resolved",
       resolve('OUT = "results/x.json"\nprint("wrote", OUT)\n')[0] == "results/x.json")
    ok("face: a join of two literals is resolved",
       resolve('OUT = os.path.join("results", "x.json")\nprint("wrote", OUT)\n')[0]
       == "results/x.json")
    ok("face: a count is refused with its own reason",
       resolve('print("wrote", len(lines))\n')[2] == U_NOT_A_PATH_VALUE)
    ok("face: a dict key is refused with its own reason",
       resolve('print("wrote %s" % face["_written"])\n')[2] == U_SUBSCRIPT)
    ok("face: an unfoldable name is refused with its own reason",
       resolve('print("wrote", path)\n')[2] == U_UNFOLDABLE_NAME)
    ok("face: a message with nothing but the word is refused",
       resolve('print("wrote state and heartbeat")\n')[2] == U_NO_SECOND_ARGUMENT)
    ok("face: a path spelled inside the message text is resolved",
       resolve('print("wrote results/x.json")\n')[0] == "results/x.json")
    ok("face: a Path constant joined from ROOT folds to a repo-relative face",
       resolve('ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
               'OUT = ROOT / "results" / "x.json"\nprint("wrote", OUT)\n')[0]
       == "results/x.json")
    ok("face: a presentation wrapper folds through to the face",
       resolve('OUT = "results/x.json"\nprint("wrote", os.path.relpath(OUT, ROOT).replace("\\\\", "/"))\n')[0]
       == "results/x.json")
    ok("face: a face built in the enclosing function is resolved",
       resolve('def main():\n'
               '    OUT = "results/x.json"\n'
               '    print("wrote", OUT)\n')[0] == "results/x.json")

    # --- classifications
    ok("spawn: a capturing spawner wins over an uncaptured one",
       classify_spawn([{"captures": True}, {"captures": False}]) == S_CAPTURED)
    ok("spawn: an uncaptured spawner is its own class",
       classify_spawn([{"captures": False}]) == S_UNCAPTURED)
    ok("spawn: no spawner is its own class", classify_spawn([]) == S_NONE)
    ok("announce: no resolvable face is unassessable, not unannounced",
       classify_announce(None, []) == A_UNASSESSABLE)
    ok("announce: a resolved face with no other announcement is message-only",
       classify_announce("results/x.json", []) == A_ONLY_MESSAGE)
    ok("announce: a pointer face is an announcement",
       classify_announce("results/x.json", [{"kind": "pointer"}]) == A_POINTER_FACE)
    ok("announce: a source literal is an announcement",
       classify_announce("results/x.json", [{"kind": "source_literal"}]) == A_SOURCE_LITERAL)
    ok("risk: message-only beside a spawnable writer is the runnable arm",
       classify_risk(S_CAPTURED, A_ONLY_MESSAGE, False) == R_MESSAGE_ONLY_RUNNABLE)
    ok("risk: message-only beside an unspawnable writer is the unrunnable arm",
       classify_risk(S_NONE, A_ONLY_MESSAGE, False) == R_MESSAGE_ONLY_UNRUNNABLE)
    ok("risk: a self re-read keeps a message-only face out of the at-risk class",
       classify_risk(S_NONE, A_ONLY_MESSAGE, True) == R_SELF_ANNOUNCING)
    ok("risk: an announced face is not at risk",
       classify_risk(S_NONE, A_POINTER_FACE, False) == R_ANNOUNCED_ELSEWHERE)
    ok("risk: unassessable is never folded into an announcement class",
       classify_risk(S_NONE, A_UNASSESSABLE, False) == R_UNASSESSABLE)

    # --- the published face
    face = build(write=False)
    rows = face["rows"]
    s = face["summary"]
    ok("face: the population is non-empty and larger than the parent's six",
       s["rows"] > 6, str(s["rows"]))
    ok("face: the spawn counts partition the rows", sum(s["by_spawn_class"].values()) == len(rows))
    ok("face: the announcement counts partition the rows",
       sum(s["by_announcement_class"].values()) == len(rows))
    ok("face: the risk counts partition the rows", sum(s["by_risk_class"].values()) == len(rows))
    ok("face: the workspace counts partition the rows",
       sum(s["by_workspace_class"].values()) == len(rows))
    ok("face: the cross-tab cells sum to the rows",
       sum(s["cross_tab_spawn_x_announce"].values()) == len(rows),
       str(sum(s["cross_tab_spawn_x_announce"].values())))
    ok("face: at-risk is the sum of its two arms",
       s["at_risk_rows"] == s["by_risk_class"][R_MESSAGE_ONLY_RUNNABLE] +
       s["by_risk_class"][R_MESSAGE_ONLY_UNRUNNABLE])
    ok("face: every row's message is the word this study measures",
       all(MESSAGE_WORD in r["render"]["text"] for r in rows))
    ok("face: face_problems is clean", face_problems(face) == [], str(face_problems(face))[:300])
    ok("face: the verdict follows the at-risk count",
       face["verdict"] == (V_SOME_AT_RISK if s["at_risk_rows"] else V_NONE_AT_RISK))

    # --- doctored copies must be refused
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    ok("defect: a hand-written verdict is refused", bool(face_problems(doc)))

    doc = json.loads(json.dumps(face))
    doc["rows"] = doc["rows"][:-1]
    ok("defect: a summary that outlives its rows is refused", bool(face_problems(doc)))

    doc = json.loads(json.dumps(face))
    doc["rows"][0]["spawn_class"] = S_CAPTURED
    ok("defect: a row called captured with no capturing spawner is refused",
       bool(face_problems(doc)))

    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["announcement_class"] == A_ONLY_MESSAGE:
            r["facts"]["announcements"] = [{"source": "someone.py", "kind": "source_literal"}]
            break
    else:
        doc["rows"][0]["announcement_class"] = A_ONLY_MESSAGE
        doc["rows"][0]["face"]["path"] = doc["rows"][0]["face"]["path"] or "results/x.json"
        doc["rows"][0]["facts"]["announcements"] = [{"source": "someone.py",
                                                     "kind": "source_literal"}]
    ok("defect: a message-only row that lists an announcement is refused",
       any("lists an announcement" in p for p in face_problems(doc)))

    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["announcement_class"] == A_UNASSESSABLE:
            r["face"]["unresolved_because"] = "a reason this study never publishes"
            break
    else:
        doc["rows"][0]["announcement_class"] = A_UNASSESSABLE
        doc["rows"][0]["face"]["path"] = None
        doc["rows"][0]["face"]["unresolved_because"] = "a reason this study never publishes"
    ok("defect: an unassessable row with no vocabulary reason is refused",
       any("vocabulary reason" in p for p in face_problems(doc)))

    doc = json.loads(json.dumps(face))
    doc["summary"]["at_risk_rows"] = s["at_risk_rows"] + 1
    ok("defect: an at-risk count that is not the rows' is refused", bool(face_problems(doc)))

    doc = json.loads(json.dumps(face))
    del doc["evidence_cutoff"]
    ok("defect: a face with no evidence_cutoff is refused", bool(face_problems(doc)))

    # --- the study must not measure its own output
    ok("self: the scan excludes this study's own source",
       not any("e554_wrote_population" in rel for rel, _ in _walk_sources()))
    ok("self: the scan excludes this study's own faces",
       not any("WROTEPOPULATION" in rel or "wrotepopulation_latest" in rel
               for rel, _ in _walk_sources((".py", ".json"))))

    print("%d/%d legs green" % (n - len(fails), n))
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        build()
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "population":
        rows = population()
        print(json.dumps({"rows": len(rows),
                          "writers": len({r["writer"] for r in rows})}, ensure_ascii=False))
        return 0
    raise SystemExit("unknown command: %s (build|check|verify|selftest|population)" % cmd)


if __name__ == "__main__":
    sys.exit(main())