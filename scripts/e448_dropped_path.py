"""E448: E442 published 85 compositions whose value is never used in the scope that composed it,
and graded none of them as superseded or lost.

A dropped composition is cheap to leave behind: `p = os.path.join(base, "x.json")` costs one line,
and whether the file is written by some *other* open in the same file is a separate question.

This study takes the 85 published rows and, per row:

  1. decides whether the row is a path composition at all (a `"\\n".join(lines)` is a text join,
     and E442's kind detector takes it as `os_path_join` because the tail is `join`);
  2. resolves the parent directory implied by the composition -- the leading parts, each of which
     must resolve through a string literal or a module-level constant of the same file;
  3. scans every opener in the same file (`open`, `read_text`, `to_csv`, `mkdir`, `load`, ...),
     resolves its path argument the same way, and asks whether it lands *under that parent*
     (a boundary-respecting prefix test, so parent `r` never matches `results/x.json`);
  4. publishes the class:

       superseded_by_a_wider_open   another open in the file lands under the same parent
                                    (basis: exact_path / same_basename_under_parent / sibling)
       opened_nowhere_in_the_file   no open in the file lands under that parent
       parent_not_resolvable        the parent is a runtime value (a temp dir, a parameter)
       not_a_path_composition       the receiver is a string constant, so it is not a path join

Usage:
    python scripts/e448_dropped_path.py run|verify|check|selftest

`check` re-derives every published tally *and every published class* from the published rows, so a
face whose classes were edited without editing the evidence is refused.
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import date

import e419_unstampable as e419

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "droppedpath_latest.json"
DATED_PREFIX = "DROPPEDPATH"
CARD = "E448-WHICH-COMPOSED-AND-DROPPED-PATH-IS-STILL-WRITTEN-BY-ANOTHER-BRANCH"
SOURCE_FACE = "deadpath_latest.json"
SOURCE_CLASS = "composed_and_never_used_in_the_scope"
SELF_SKIP = ("e448", "run_e448")
MAX_TEXT = 160

K_SAME = "superseded_by_a_wider_open"
K_ORPHAN = "opened_nowhere_in_the_file"
K_NO_PARENT = "parent_not_resolvable"
K_NOT_PATH = "not_a_path_composition"
CLASS_VOCAB = (K_SAME, K_ORPHAN, K_NO_PARENT, K_NOT_PATH)

B_EXACT = "exact_path"
B_NAME = "same_basename_under_parent"
B_SIBLING = "sibling_under_parent"
BASIS_VOCAB = (B_EXACT, B_NAME, B_SIBLING)

V_NONE = "no_dropped_composition_was_published"
V_ALL = "every_dropped_path_composition_is_opened_by_another_open_in_its_file"
V_SOME = "some_dropped_path_compositions_are_opened_nowhere_in_their_file"
V_UNGRADABLE = "no_dropped_composition_is_a_gradable_path_composition"
VERDICT_VOCAB = (V_NONE, V_ALL, V_SOME, V_UNGRADABLE)

WRITE_TAILS = frozenset({
    "to_csv", "to_parquet", "to_json", "to_excel", "write_text", "write_bytes", "writelines",
    "save", "savefig", "dump", "savez", "savez_compressed", "mkdir", "makedirs", "remove",
    "unlink", "rmtree", "rename", "replace", "copy", "copyfile", "copy2", "move",
})
READ_TAILS = frozenset({
    "read_text", "read_bytes", "readlines", "load", "loads", "read_csv", "read_parquet",
    "read_json", "read_excel", "read_table", "read_feather", "read_pickle", "getsize",
    "getmtime", "isfile", "isdir", "exists", "openpyxl_load", "loadtxt", "load_workbook",
})
DIR_TAILS = frozenset({"listdir", "scandir", "walk", "glob", "iglob", "iterdir", "rglob"})
OPENER_TAILS = frozenset(WRITE_TAILS | READ_TAILS | DIR_TAILS | {"open", "loadtxt"})
# pathlib methods carry the path in the receiver, not in an argument: `p.write_text(s)`.
PATH_METHOD_TAILS = frozenset({
    "write_text", "read_text", "write_bytes", "read_bytes", "open", "exists", "unlink",
    "mkdir", "touch", "iterdir", "glob", "rglob", "is_file", "is_dir",
})
PATH_KWARGS = ("path", "file", "fname", "filename", "name", "p", "src", "dst", "out")


# --------------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------------
def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _dump(path: str, face: dict) -> None:
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def corpus() -> list[str]:
    """E419's census scope minus this study's own files (the self-inclusion law, E180/E207)."""
    return [p for p in e419.corpus() if not os.path.basename(p).startswith(SELF_SKIP)]


def _tail(node) -> str:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _dotted(node) -> str:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def _slashes(text: str) -> str:
    out = text.replace("\\", "/")
    while "//" in out:
        out = out.replace("//", "/")
    if len(out) > 1 and out.endswith("/"):
        out = out.rstrip("/")
    return out


def _key(text: str | None) -> str | None:
    """The comparison key: repository-relative when the path is anchored at the repo root."""
    if text is None:
        return None
    if not isinstance(text, str):
        return None
    out = _slashes(text)
    root = _slashes(ROOT)
    if out == root:
        return ""
    if out.lower().startswith(root.lower() + "/"):
        out = out[len(root) + 1:]
    elif out.startswith("<ROOT>"):
        out = out[len("<ROOT>"):].lstrip("/")
    return out


def _join_values(values: list[str]) -> str:
    head = values[0]
    for part in values[1:]:
        if not part:
            continue
        if head in ("", "."):
            head = part
        elif part in (".", ""):
            continue
        else:
            head = head.rstrip("/") + "/" + part.lstrip("/")
    return head


def _dirname(value: str) -> str:
    out = _slashes(value)
    if "/" not in out:
        return ""
    return out.rsplit("/", 1)[0]


# --------------------------------------------------------------------------------------------
# resolution
# --------------------------------------------------------------------------------------------
def _resolve(node, env: dict, depth: int = 0):
    """Best-effort string value of a path expression; None means 'this is a runtime value'."""
    if node is None or depth > 10:
        return None
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            # the module's own file, so that dirname(dirname(abspath(__file__))) lands where the
            # authored code lands: anchoring it at the repo root moved every ROOT up one level
            return env.get("__file__") if isinstance(env.get("__file__"), str) else ROOT + "/_file_.py"
        value = env.get(node.id)
        return value if isinstance(value, str) else None
    if isinstance(node, ast.JoinedStr):
        out: list[str] = []
        for piece in node.values:
            if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                out.append(piece.value)
            else:
                return None
        return "".join(out)
    if isinstance(node, ast.Attribute):
        if node.attr == "parent":
            base = _resolve(node.value, env, depth + 1)
            return _dirname(base) if isinstance(base, str) else None
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _resolve(node.left, env, depth + 1)
        right = _resolve(node.right, env, depth + 1)
        if not isinstance(left, str) or not isinstance(right, str):
            return None
        return _join_values([left, right])
    if isinstance(node, ast.Call):
        tail = _tail(node.func)
        dotted = _dotted(node.func)
        if tail in ("mkdtemp", "mkstemp", "TemporaryDirectory", "NamedTemporaryFile", "tempdir"):
            return None
        if tail == "join" or tail == "joinpath":
            is_path_join = (
                tail == "joinpath"
                or dotted in ("join", "os.path.join", "posixpath.join", "ntpath.join", "path.join")
                or dotted.endswith(".path.join")
            )
            if not is_path_join:
                return None
            values = [_resolve(arg, env, depth + 1) for arg in node.args]
            if not values or any(not isinstance(v, str) for v in values):
                return None
            return _join_values(values)  # type: ignore[arg-type]
        if tail == "dirname":
            base = _resolve(node.args[0], env, depth + 1) if node.args else None
            return _dirname(base) if isinstance(base, str) else None
        if tail in ("abspath", "normpath", "expanduser", "absolute", "resolve", "str", "fspath"):
            base = _resolve(node.args[0], env, depth + 1) if node.args else None
            return base if isinstance(base, str) else None
        if tail in ("Path", "PurePath", "PosixPath", "WindowsPath"):
            base = _resolve(node.args[0], env, depth + 1) if node.args else None
            return base if isinstance(base, str) else None
        return None
    return None


def const_env(tree, rel: str = "") -> dict:
    """Module-level string constants, resolved in order (a later name may use an earlier one)."""
    env: dict = {"__file__": (ROOT + "/" + rel) if rel else (ROOT + "/_file_.py")}
    for stmt in tree.body:
        target = None
        value = None
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            target, value = stmt.targets[0].id, stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
            target, value = stmt.target.id, stmt.value
        if target is not None:
            env[target] = _resolve(value, env)
    return env


def composition_parts(node) -> list | None:
    """The parts of a path composition, or None when the expression is not one.

    A `"\\n".join(lines)` is a text join whose receiver is a string constant; E442's kind detector
    classes it as `os_path_join` because the dotted tail is `join`, so it is excluded here and
    published as `not_a_path_composition` rather than silently graded as a path.
    """
    if isinstance(node, ast.Call) and _tail(node.func) == "join":
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Constant):
            return None
        dotted = _dotted(func)
        if dotted.endswith("path.join") or dotted in ("join", "posixpath.join", "ntpath.join"):
            return list(node.args) or None
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        parts: list = []
        cur = node
        while isinstance(cur, ast.BinOp) and isinstance(cur.op, ast.Div):
            parts.append(cur.right)
            cur = cur.left
        parts.append(cur)
        parts.reverse()
        return parts
    return None


def _mode_of(tail: str, node) -> str:
    if tail == "open":
        mode = None
        if len(node.args) > 1:
            mode = _resolve(node.args[1], {})
        for kw in node.keywords:
            if kw.arg == "mode":
                mode = _resolve(kw.value, {})
        if isinstance(mode, str) and any(ch in mode for ch in "wax+"):
            return "write"
        return "read"
    if tail in WRITE_TAILS:
        return "write"
    if tail in DIR_TAILS:
        return "dir"
    return "read"


def opener_index(tree, env: dict) -> list[dict]:
    """Every opener call in the file, with its path resolved to a comparison key where possible."""
    out: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        tail = _tail(node.func)
        if tail not in OPENER_TAILS:
            continue
        arg = None
        if isinstance(node.func, ast.Attribute) and tail in PATH_METHOD_TAILS:
            arg = node.func.value
        if arg is None and node.args:
            arg = node.args[0]
        if arg is None:
            for kw in node.keywords:
                if kw.arg in PATH_KWARGS:
                    arg = kw.value
                    break
        if arg is None:
            continue
        value = _resolve(arg, env)
        if value is None:
            parts = composition_parts(arg)
            if parts:
                values = [_resolve(p, env) for p in parts]
                if values and all(isinstance(v, str) for v in values):
                    value = _join_values(values)  # type: ignore[arg-type]
        out.append({
            "line": int(getattr(node, "lineno", 0) or 0),
            "callee": _dotted(node.func)[-48:],
            "mode": _mode_of(tail, node),
            "key": _key(value),
        })
    out.sort(key=lambda o: (o["line"], o["callee"]))
    return out


# --------------------------------------------------------------------------------------------
# grading
# --------------------------------------------------------------------------------------------
def under_parent(key: str | None, parent: str | None) -> bool:
    """Boundary-respecting: parent `r` does not cover `results/x.json`."""
    if key is None or parent is None:
        return False
    if parent == "":
        return key != ""
    return key == parent or key.startswith(parent + "/")


def _basis(key: str, parent: str, composed: str | None, name: str | None) -> str:
    if composed is not None and key == composed:
        return B_EXACT
    leaf = key.rsplit("/", 1)[-1]
    if name is not None and leaf == name:
        return B_NAME
    return B_SIBLING


def _in_git(key: str | None) -> bool:
    if not key:
        return False
    return ".git" in key.split("/")


def _on_disk(composed: str | None):
    """Does the composed path exist right now? A read-only probe, never a write.

    This separates two readings of the same orphan: the artifact exists and something else
    produced it (a hand-written prereg note, another writer), or the path was never produced.
    """
    if not composed:
        return None
    if any(ch in composed for ch in "*?["):
        # a glob pattern is not a path: probing the literal would report 'absent' for a pattern
        return None
    path = composed if (len(composed) > 2 and composed[1] == ":" or composed.startswith("/")) \
        else os.path.join(ROOT, composed)
    try:
        return os.path.exists(path)
    except OSError:
        return None


def grade_site(rel: str, src: str, expression: str, env: dict | None = None,
               openers: list[dict] | None = None) -> dict:
    """Grade one published dropped composition against the openers of its own file."""
    row: dict = {
        "file": rel,
        "expression": " ".join(expression.split())[:MAX_TEXT],
        "composed_key": None,
        "parent_key": None,
        "parent_resolved": False,
        "openers_in_file": 0,
        "hits": [],
        "ignored_hits": [],
        "class": K_NO_PARENT,
        "basis": None,
        "on_disk": None,
    }
    try:
        node = ast.parse(expression, mode="eval").body
    except SyntaxError:
        row["class"] = K_NOT_PATH
        row["note"] = "the published expression does not parse on its own"
        return row
    if env is None or openers is None:
        try:
            tree = ast.parse(src)
        except SyntaxError:
            row["class"] = K_NOT_PATH
            row["note"] = "the file does not parse"
            return row
        env = const_env(tree, rel)
        openers = opener_index(tree, env)
    row["openers_in_file"] = len(openers)

    parts = composition_parts(node)
    if not parts:
        row["class"] = K_NOT_PATH
        row["note"] = "the receiver is a string constant: this is a text join, not a path"
        return row
    if len(parts) < 2:
        row["class"] = K_NO_PARENT
        row["note"] = "a one-part composition has no parent to grade against"
        return row

    composed_values = [_resolve(p, env) for p in parts]
    composed = (_join_values(composed_values)  # type: ignore[arg-type]
                if all(isinstance(v, str) for v in composed_values) else None)
    row["composed_key"] = _key(composed)
    name = _resolve(parts[-1], env)
    parent_values = composed_values[:-1]
    if all(isinstance(v, str) for v in parent_values):
        parent = _key(_join_values(parent_values))  # type: ignore[arg-type]
        row["parent_key"] = parent
        row["parent_resolved"] = parent is not None
    if not row["parent_resolved"]:
        row["class"] = K_NO_PARENT
        return row

    parent = row["parent_key"]
    hits = []
    ignored = []
    for opener in openers:
        if not under_parent(opener.get("key"), parent):
            continue
        if opener.get("key") == parent and opener.get("mode") != "dir":
            # an opener that names the directory itself is not an open *under* it
            continue
        entry = {
            "line": opener["line"],
            "callee": opener["callee"],
            "mode": opener["mode"],
            "key": opener["key"],
        }
        if _in_git(entry["key"]):
            # a git plumbing write (`rebase-merge/author-script`) says nothing about whether
            # this file's own artifact is produced; it is published, not counted as a hit
            ignored.append(entry)
            continue
        entry["basis"] = _basis(opener["key"], parent, row["composed_key"],
                                name if isinstance(name, str) else None)
        hits.append(entry)
    row["hits"] = hits
    row["ignored_hits"] = ignored
    row["on_disk"] = _on_disk(row["composed_key"])
    if hits:
        row["class"] = K_SAME
        order = {B_EXACT: 0, B_NAME: 1, B_SIBLING: 2}
        row["basis"] = sorted(hits, key=lambda h: order[h["basis"]])[0]["basis"]
    else:
        row["class"] = K_ORPHAN
    return row


def _file_cache(cutoff: str | None = None) -> dict:
    """Parse every file the population names once (the population is 85 rows over 69 files)."""
    cache: dict = {}
    for rel in corpus():
        try:
            src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        env = const_env(tree, rel)
        cache[rel] = {"src": src, "env": env, "openers": opener_index(tree, env)}
    return cache


def population() -> tuple[list[dict], dict]:
    face = _load(os.path.join(ST, SOURCE_FACE))
    rows = [r for r in (face.get("rows") or []) if r.get("consumption") == SOURCE_CLASS]
    rows.sort(key=lambda r: (r["file"], r["line"], r.get("col", 0)))
    return rows, {"face": SOURCE_FACE, "evidence_cutoff": face.get("evidence_cutoff"),
                  "population": len(rows)}


def build(cutoff: str | None = None) -> dict:
    cutoff = cutoff or date.today().isoformat()
    source_rows, source = population()
    cache = _file_cache()
    rows: list[dict] = []
    for src_row in source_rows:
        rel = src_row["file"]
        entry = cache.get(rel)
        if entry is None:
            rows.append({
                "file": rel,
                "line": src_row["line"],
                "col": src_row.get("col", 0),
                "scope": src_row.get("scope"),
                "binding": src_row.get("binding"),
                "expression": " ".join(str(src_row.get("expression") or "").split())[:MAX_TEXT],
                "composed_key": None,
                "parent_key": None,
                "parent_resolved": False,
                "openers_in_file": 0,
                "hits": [],
                "ignored_hits": [],
                "class": K_NO_PARENT,
                "basis": None,
                "on_disk": None,
                "note": "the file named by the published row is not in the corpus walk",
            })
            continue
        graded = grade_site(rel, entry["src"], str(src_row.get("expression") or ""),
                            entry["env"], entry["openers"])
        graded["line"] = src_row["line"]
        graded["col"] = src_row.get("col", 0)
        graded["scope"] = src_row.get("scope")
        graded["binding"] = src_row.get("binding")
        rows.append(graded)
    rows.sort(key=lambda r: (r["file"], r.get("line") or 0))
    return face_of(rows, source, cutoff)


def _tally(rows: list[dict], key: str, vocab) -> dict:
    out = {v: 0 for v in vocab}
    for r in rows:
        v = r.get(key)
        out[v] = out.get(v, 0) + 1
    return out


def verdict_for(rows: list[dict]) -> str:
    if not rows:
        return V_NONE
    by_class = _tally(rows, "class", CLASS_VOCAB)
    graded = by_class[K_SAME] + by_class[K_ORPHAN]
    if graded == 0:
        return V_UNGRADABLE
    if by_class[K_ORPHAN] > 0:
        return V_SOME
    return V_ALL


def face_of(rows: list[dict], source: dict, cutoff: str) -> dict:
    by_class = _tally(rows, "class", CLASS_VOCAB)
    by_basis = _tally([r for r in rows if r.get("basis")], "basis", BASIS_VOCAB)
    by_file: dict[str, int] = {}
    for r in rows:
        by_file[r["file"]] = by_file.get(r["file"], 0) + 1
    parents: dict[str, int] = {}
    for r in rows:
        if r.get("parent_resolved"):
            parents[r["parent_key"]] = parents.get(r["parent_key"], 0) + 1
    orphans = [{"file": r["file"], "line": r.get("line"), "expression": r["expression"],
                "parent_key": r.get("parent_key"), "openers_in_file": r.get("openers_in_file")}
               for r in rows if r["class"] == K_ORPHAN]
    unresolvable = [{"file": r["file"], "line": r.get("line"), "expression": r["expression"],
                     "parent_key": r.get("parent_key")}
                    for r in rows if r["class"] == K_NO_PARENT]
    not_path = [{"file": r["file"], "line": r.get("line"), "expression": r["expression"]}
                for r in rows if r["class"] == K_NOT_PATH]
    summary = {
        "population": len(rows),
        "source_face": source,
        "by_class": by_class,
        "by_basis": by_basis,
        "files_with_a_dropped_site": len(by_file),
        "superseded_sites": by_class[K_SAME],
        "orphan_sites": by_class[K_ORPHAN],
        "parent_not_resolvable_sites": by_class[K_NO_PARENT],
        "not_a_path_composition_sites": by_class[K_NOT_PATH],
        "superseded_by_an_open_of_the_same_path": by_basis[B_EXACT],
        "superseded_by_a_same_named_open": by_basis[B_NAME],
        "superseded_by_a_sibling_open_only": by_basis[B_SIBLING],
        "orphans": orphans,
        "parent_not_resolvable": unresolvable,
        "not_a_path_composition": not_path,
        "parents_by_dropped_sites": dict(sorted(parents.items(), key=lambda kv: (-kv[1], kv[0]))),
        "openers_scanned": sum(int(r.get("openers_in_file") or 0) for r in rows),
        "hits_ignored_as_git_plumbing": sum(len(r.get("ignored_hits") or []) for r in rows),
        "orphan_paths_already_on_disk": sum(1 for r in rows if r["class"] == K_ORPHAN
                                            and r.get("on_disk") is True),
        "orphan_paths_absent_from_disk": sum(1 for r in rows if r["class"] == K_ORPHAN
                                             and r.get("on_disk") is False),
        "orphan_paths_not_checkable": sum(1 for r in rows if r["class"] == K_ORPHAN
                                          and r.get("on_disk") is None),
        "orphan_paths_that_are_a_glob_pattern": sum(
            1 for r in rows if r["class"] == K_ORPHAN and r.get("composed_key")
            and any(ch in r["composed_key"] for ch in "*?[")),
    }
    return {
        "study": "E448_which_composed_and_dropped_path_is_still_written_by_another_branch",
        "card": CARD,
        "title": "the 85 dropped path compositions of E442, graded as superseded by another open "
                 "in the same file or as opened nowhere",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff,
        "verdict": verdict_for(rows),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "the parent is a string prefix of the composed key, not a filesystem question: a "
            "parent that a `..` segment or a glob pattern defeats is graded as if it were literal",
            "resolution only follows a string literal or a module-level constant of the same "
            "file; a parent built from a parameter, a temp dir or a config read is published as "
            "parent_not_resolvable and is never counted as an orphan",
            "superseded means 'some open in this file lands under that parent' -- it does not "
            "mean the intended artifact exists; the basis column separates an exact re-open of "
            "the same path from a sibling open, and a file that writes many artifacts under one "
            "parent will mark every drop there as superseded",
            "openers are recognised by a frozen tail vocabulary (open/read_*/write_*/to_*/load/"
            "dump/mkdir/remove/...); an opener reached through an alias (`op = open`) is not in it",
            "a text join is only excluded when the receiver is a string constant; `sep.join(...)` "
            "on a variable receiver is still read as a path composition",
            "static only: nothing is executed, so an open performed inside a helper called from "
            "this file is invisible here",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(ST, exist_ok=True)
    path = os.path.join(ST, FACE_NAME)
    dated = os.path.join(ST, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))
    _dump(path, face)
    _dump(dated, face)
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not isinstance(rows, list):
        return ["rows is not a list"]
    by_class = {c: 0 for c in CLASS_VOCAB}
    by_basis = {b: 0 for b in BASIS_VOCAB}
    by_file: dict[str, int] = {}
    parents: dict[str, int] = {}
    for r in rows:
        cls = r.get("class")
        where = "%s:%s" % (r.get("file"), r.get("line"))
        if cls not in CLASS_VOCAB:
            problems.append("%s class outside the vocabulary" % where)
            continue
        by_class[cls] += 1
        by_file[r["file"]] = by_file.get(r["file"], 0) + 1
        if r.get("basis"):
            if r["basis"] not in BASIS_VOCAB:
                problems.append("%s basis outside the vocabulary" % where)
            else:
                by_basis[r["basis"]] += 1
        if r.get("parent_resolved") and r.get("parent_key") is not None:
            parents[r["parent_key"]] = parents.get(r["parent_key"], 0) + 1
        # --- the class must re-derive from the row's own evidence ---
        hits = r.get("hits") or []
        if cls == K_NOT_PATH:
            if r.get("parent_resolved") or hits:
                problems.append("%s is not a path composition but carries a parent or hits" % where)
            if r.get("basis"):
                problems.append("%s is not a path composition but carries a basis" % where)
            continue
        if cls == K_NO_PARENT:
            if r.get("parent_resolved"):
                problems.append("%s has an unresolvable parent but carries parent_resolved" % where)
            if hits:
                problems.append("%s has an unresolvable parent but carries hits" % where)
            continue
        if not r.get("parent_resolved"):
            problems.append("%s is graded against a parent it did not resolve" % where)
            continue
        parent = r.get("parent_key")
        composed = r.get("composed_key")
        for hit in hits:
            if _in_git(hit.get("key")):
                problems.append("%s counts a git plumbing open as a hit" % where)
            if not under_parent(hit.get("key"), parent):
                problems.append("%s hit %s is outside parent %r" % (where, hit.get("key"), parent))
            if hit.get("basis") not in BASIS_VOCAB:
                problems.append("%s hit basis outside the vocabulary" % where)
                continue
            expected = _basis(hit["key"], parent or "", composed,
                              (composed.rsplit("/", 1)[-1] if composed else None))
            if hit["basis"] != expected:
                problems.append("%s hit %s claims basis %s, derives %s"
                                % (where, hit.get("key"), hit.get("basis"), expected))
        if cls == K_SAME and not hits:
            problems.append("%s is superseded with no open under its parent" % where)
        if cls == K_ORPHAN and hits:
            problems.append("%s is an orphan but carries %d hit(s)" % (where, len(hits)))
        if cls == K_ORPHAN and r.get("basis"):
            problems.append("%s is an orphan but carries a basis" % where)
        if hits:
            order = {B_EXACT: 0, B_NAME: 1, B_SIBLING: 2}
            expected_basis = sorted(hits, key=lambda h: order.get(h["basis"], 9))[0]["basis"]
            if r.get("basis") != expected_basis:
                problems.append("%s basis does not re-derive from its hits" % where)
    if by_class != (s.get("by_class") or {}):
        problems.append("by_class does not re-derive from the rows")
    if by_basis != (s.get("by_basis") or {}):
        problems.append("by_basis does not re-derive from the rows")
    if len(by_file) != (s.get("files_with_a_dropped_site") or 0):
        problems.append("files_with_a_dropped_site does not re-derive")
    if dict(sorted(parents.items(), key=lambda kv: (-kv[1], kv[0]))) != (s.get("parents_by_dropped_sites") or {}):
        problems.append("parents_by_dropped_sites does not re-derive")
    if sum(by_class.values()) != (s.get("population") or 0):
        problems.append("the class tally does not close over the population")
    if len(rows) != (s.get("population") or 0):
        problems.append("population does not equal the number of rows")
    src = s.get("source_face") or {}
    if src.get("population") != len(rows):
        problems.append("the published population does not match the source face it names")
    for key in ("superseded_sites", "orphan_sites", "parent_not_resolvable_sites",
                "not_a_path_composition_sites"):
        want = {"superseded_sites": K_SAME, "orphan_sites": K_ORPHAN,
                "parent_not_resolvable_sites": K_NO_PARENT,
                "not_a_path_composition_sites": K_NOT_PATH}[key]
        if s.get(key) != by_class[want]:
            problems.append("%s does not re-derive" % key)
    if s.get("superseded_by_an_open_of_the_same_path") != by_basis[B_EXACT]:
        problems.append("superseded_by_an_open_of_the_same_path does not re-derive")
    if s.get("superseded_by_a_sibling_open_only") != by_basis[B_SIBLING]:
        problems.append("superseded_by_a_sibling_open_only does not re-derive")
    orphan_rows = [r for r in rows if r.get("class") == K_ORPHAN]
    if len(s.get("orphans") or []) != len(orphan_rows):
        problems.append("the orphan list does not equal the orphan rows")
    ignored = sum(len(r.get("ignored_hits") or []) for r in rows)
    if ignored != (s.get("hits_ignored_as_git_plumbing") or 0):
        problems.append("hits_ignored_as_git_plumbing does not re-derive")
    for key, want in (("orphan_paths_already_on_disk", True),
                      ("orphan_paths_absent_from_disk", False),
                      ("orphan_paths_not_checkable", None)):
        derived = sum(1 for r in rows if r.get("class") == K_ORPHAN and r.get("on_disk") is want)
        if derived != (s.get(key) or 0):
            problems.append("%s does not re-derive" % key)
    globs = sum(1 for r in rows if r.get("class") == K_ORPHAN and r.get("composed_key")
                and any(ch in r["composed_key"] for ch in "*?["))
    if globs != (s.get("orphan_paths_that_are_a_glob_pattern") or 0):
        problems.append("orphan_paths_that_are_a_glob_pattern does not re-derive")
    for r in rows:
        key = r.get("composed_key")
        if key and any(ch in key for ch in "*?[") and r.get("on_disk") is not None:
            problems.append("%s:%s probes a glob pattern as if it were a path"
                            % (r.get("file"), r.get("line")))
    if verdict_for(rows) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the published rows")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(ST, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    for key in ("population", "by_class", "by_basis", "orphan_sites", "superseded_sites"):
        if live["summary"].get(key) != face["summary"].get(key):
            problems.append("live %s differs from the published face" % key)
    published = {(r["file"], r.get("line")): r.get("class") for r in face.get("rows") or []}
    rebuilt = {(r["file"], r.get("line")): r.get("class") for r in live.get("rows") or []}
    if published != rebuilt:
        moved = sorted(set(published.items()) ^ set(rebuilt.items()))[:5]
        problems.append("the rebuilt classes differ at %d site(s), e.g. %s"
                        % (len(set(published.items()) ^ set(rebuilt.items())), moved))
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    def grade(src: str, expression: str) -> dict:
        return grade_site("scripts/fixture.py", src, expression)

    # 1: a sibling open under the same parent supersedes the drop
    g = grade("import os\np = os.path.join('results', 'x', 'a.json')\n"
              "open(os.path.join('results', 'x', 'b.json'), 'w')\n",
              "os.path.join('results', 'x', 'a.json')")
    check("sibling_open_supersedes", g["class"] == K_SAME and g["basis"] == B_SIBLING)
    # 2: the same path opened elsewhere is the strongest basis
    g = grade("import os\np = os.path.join('results', 'x', 'a.json')\n"
              "open(os.path.join('results', 'x', 'a.json'), 'w')\n",
              "os.path.join('results', 'x', 'a.json')")
    check("exact_reopen_is_the_first_basis", g["class"] == K_SAME and g["basis"] == B_EXACT)
    # 3: a same-named file elsewhere is not under this parent
    g = grade("import os\np = os.path.join('results', 'y', 'a.json')\n"
              "open(os.path.join('results', 'x', 'a.json'), 'w')\n",
              "os.path.join('results', 'y', 'a.json')")
    check("other_parent_is_an_orphan", g["class"] == K_ORPHAN and g["hits"] == [])
    # 4: the prefix boundary -- parent 'r' must not cover 'results/x.json'
    g = grade("import os\np = os.path.join('r', 'a.json')\n"
              "open(os.path.join('results', 'x.json'), 'w')\n",
              "os.path.join('r', 'a.json')")
    check("prefix_is_boundary_respecting", g["class"] == K_ORPHAN)
    # 5: a runtime base is published unresolvable, never an orphan
    g = grade("import os\ndef f(tmp):\n    p = os.path.join(tmp, 'a.json')\n",
              "os.path.join(tmp, 'a.json')")
    check("runtime_base_is_not_graded_as_orphan",
          g["class"] == K_NO_PARENT and g["parent_resolved"] is False)
    # 6: a module constant is resolved through the file's own assignments, and __file__ is anchored
    # at the module's own path so that dirname(dirname(abspath(__file__))) is the repo root
    g = grade("import os\nROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
              "p = os.path.join(ROOT, 'results', 'a.json')\n"
              "open(os.path.join(ROOT, 'results', 'b.csv'), 'w')\n",
              "os.path.join(ROOT, 'results', 'a.json')")
    check("module_constant_resolves", g["class"] == K_SAME and g["parent_key"] == "results")
    # 6b: one dirname stays inside scripts/ -- the anchor is the module's file, not the root
    g = grade("import os\nHERE = os.path.dirname(os.path.abspath(__file__))\n"
              "p = os.path.join(HERE, 'a.json')\n",
              "os.path.join(HERE, 'a.json')")
    check("a_single_dirname_stays_in_scripts", g["parent_key"] == "scripts")
    # 7: a text join is not a path composition
    g = grade("lines = []\np = '\\n'.join(lines)\n", "'\\n'.join(lines)")
    check("text_join_is_not_a_path", g["class"] == K_NOT_PATH)
    # 8: Path division is a composition
    g = grade("from pathlib import Path\np = Path('out') / 'a.json'\n"
              "(Path('out') / 'b.json').write_text('x')\n",
              "Path('out') / 'a.json'")
    check("path_division_is_graded", g["class"] == K_SAME)
    # 9: an open of the parent directory itself is not an open under it
    g = grade("import os\np = os.path.join('results', 'a.json')\n"
              "os.makedirs('results')\n",
              "os.path.join('results', 'a.json')")
    check("the_parent_itself_is_not_a_hit", g["class"] == K_ORPHAN)
    # 10: a join nested in the opener argument resolves as one path
    g = grade("import os\np = os.path.join('results', 'x', 'a.json')\n"
              "open(os.path.join('results', 'x', 'sub', 'b.json'), 'w')\n",
              "os.path.join('results', 'x', 'a.json')")
    check("nested_join_argument_resolves", g["class"] == K_SAME)
    # 10b: a git plumbing write under the same parent is published, not counted as a hit
    g = grade("import os\np = os.path.join('repo', 'a.json')\n"
              "open('repo/.git/rebase-merge/author-script')\n",
              "os.path.join('repo', 'a.json')")
    check("git_plumbing_is_not_a_supersession",
          g["class"] == K_ORPHAN and len(g["ignored_hits"]) == 1 and not g["hits"])
    # 11-13: the tally refuses a doctored face
    rows = [
        {"file": "scripts/a.py", "line": 1, "expression": "os.path.join('r', 'a')",
         "composed_key": "r/a", "parent_key": "r", "parent_resolved": True,
         "openers_in_file": 1, "class": K_SAME, "basis": B_EXACT,
         "hits": [{"line": 2, "callee": "open", "mode": "write", "key": "r/a", "basis": B_EXACT}]},
        {"file": "scripts/b.py", "line": 3, "expression": "os.path.join('r', 'c')",
         "composed_key": None, "parent_key": None, "parent_resolved": False,
         "openers_in_file": 0, "class": K_NO_PARENT, "basis": None, "hits": []},
    ]
    source = {"face": SOURCE_FACE, "evidence_cutoff": "2026-11-06", "population": 2}
    face = face_of([dict(r) for r in rows], source, "2026-11-06")
    check("fixture_face_is_clean", tally_problems(face) == [])
    bad = json.loads(json.dumps(face))
    bad["summary"]["orphan_sites"] = 1
    check("tally_catches_a_wrong_orphan_count", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(face))
    bad2["rows"][0]["class"] = K_ORPHAN
    check("tally_catches_a_class_edited_off_its_evidence", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(face))
    bad3["rows"][0]["hits"][0]["key"] = "results/x/a"
    check("tally_catches_a_hit_outside_the_parent", tally_problems(bad3) != [])
    bad4 = json.loads(json.dumps(face))
    bad4["verdict"] = V_ALL
    bad4["rows"][0]["class"] = K_ORPHAN
    bad4["rows"][0]["hits"] = []
    bad4["rows"][0]["basis"] = None
    check("tally_catches_a_carried_verdict", tally_problems(bad4) != [])
    # 14: the corpus excludes this study's own files
    names = corpus()
    check("corpus_excludes_self", not any(os.path.basename(n).startswith(SELF_SKIP) for n in names))
    check("corpus_is_nonempty", len(names) > 100)

    for name in fails:
        print("FAIL", name)
    print("selftest %d/%d" % (legs - len(fails), legs))
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("verdict: %s" % face["verdict"])
        print(json.dumps(s["by_class"], ensure_ascii=False))
        print(json.dumps(s["by_basis"], ensure_ascii=False))
        print("%d dropped site(s) over %d file(s): superseded %d, orphan %d, "
              "unresolvable %d, not-a-path %d"
              % (s["population"], s["files_with_a_dropped_site"], s["superseded_sites"],
                 s["orphan_sites"], s["parent_not_resolvable_sites"],
                 s["not_a_path_composition_sites"]))
        print("face: %s" % _rel(path))
        problems = tally_problems(face)
        if problems:
            for p in problems:
                print("PROBLEM", p)
            return 1
        return 0
    if cmd == "verify":
        problems = verify()
        print("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 1 if problems else 0
    if cmd == "check":
        face = _load(os.path.join(ST, FACE_NAME))
        problems = tally_problems(face)
        if face.get("verdict") not in VERDICT_VOCAB:
            problems.append("the published verdict is not in the study's vocabulary")
        print("check problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 1 if problems else 0
    print("usage: run|verify|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))