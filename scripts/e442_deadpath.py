"""E442: E436 found 18 corpus sites that compose a path and never graded whether the composed
value is consumed or simply dropped inside the function that built it.

A composition is cheap to write and easy to leave behind: `p = os.path.join(base, name)` costs one
line, and whether anything ever opens `p` is a different question from whether the path is right.
This study takes every composition site in the corpus -- an `os.path.join(...)` call or a
`Path(...) / "x"` division -- and follows the composed value inside the scope that built it:

  consumption --
    consumed_at_the_call_site_by_an_opener   the join is an argument to open/load/dump/...
    consumed_at_the_call_site_by_a_helper    the join is an argument to some other call
    flows_into_an_open_read_or_write         the bound name reaches an opener's argument
    flows_into_a_dict_literal                the bound name sits in a dict literal (a payload)
    flows_into_a_return                      the bound name is returned
    flows_into_another_call                  the bound name is passed to some other call
    flows_into_a_nested_scope                the bound name is only read inside a nested def/lambda
    used_only_to_ask_a_question_about_the_path   p.exists() / p.parent / p.suffix and the like
    used_some_way_that_is_not_a_consumer      formatted, compared, subscripted, iterated
    stored_directly_into_a_slot_or_attribute  cfg["p"] = join(...) / self.p = join(...)
    part_of_a_larger_composition             the join is an argument to another join/division
    composed_and_never_used_in_the_scope     the bound name has no read in its scope at all
    composed_where_no_name_can_be_followed   a bare expression statement or an unpacked target

Usage:
    python scripts/e442_deadpath.py run|verify|check|selftest

`run` rescans the corpus (~3.4k sources, ~40 s) and publishes the face; `check` re-derives every
published tally from the published rows (what the S6 chain runs); `verify` rescans and compares.
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import date

import e419_unstampable as e419
import e429_two_hop_writer as e420

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST
FACE_NAME = "deadpath_latest.json"
DATED_PREFIX = "DEADPATH"
CARD = "E442-WHICH-PATH-COMPOSITION-IS-NEVER-CONSUMED"
MAX_TEXT = 160
SELF_SKIP = ("e442", "run_e442")

K_JOIN = "os_path_join"
K_DIV = "path_division"
KIND_VOCAB = (K_JOIN, K_DIV)

C_AT_OPENER = "consumed_at_the_call_site_by_an_opener"
C_AT_HELPER = "consumed_at_the_call_site_by_a_helper"
C_OPEN = "flows_into_an_open_read_or_write"
C_DICT = "flows_into_a_dict_literal"
C_RETURN = "flows_into_a_return"
C_HELPER = "flows_into_another_call"
C_CLOSURE = "flows_into_a_nested_scope"
C_QUESTION = "used_only_to_ask_a_question_about_the_path"
C_OTHER = "used_some_way_that_is_not_a_consumer"
C_SLOT = "stored_directly_into_a_slot_or_attribute"
C_NESTED = "part_of_a_larger_composition"
C_DROPPED = "composed_and_never_used_in_the_scope"
C_UNBOUND = "composed_where_no_name_can_be_followed"
CONSUMPTION_VOCAB = (
    C_AT_OPENER, C_AT_HELPER, C_OPEN, C_DICT, C_RETURN, C_HELPER, C_CLOSURE, C_QUESTION,
    C_OTHER, C_SLOT, C_NESTED, C_DROPPED, C_UNBOUND,
)
# The classes that open, read, write or hand the value to a payload -- a composed path in one of
# these classes reaches something.  The rest are published so the drop is visible, not hidden.
REACHING = frozenset({C_AT_OPENER, C_AT_HELPER, C_OPEN, C_DICT, C_RETURN, C_HELPER, C_CLOSURE})
DROPPED = frozenset({C_DROPPED, C_UNBOUND})

V_NONE = "no_path_composition_was_found"
V_ALL = "every_composed_path_reaches_a_consumer_from_where_it_is_composed"
V_SOME = "some_composed_paths_are_dropped_inside_the_scope_that_composes_them"
VERDICT_VOCAB = (V_NONE, V_ALL, V_SOME)

OPEN_RW_TAILS = frozenset({
    "open", "read_text", "read_bytes", "write_text", "write_bytes", "write", "writelines",
    "load", "dump", "loads", "dumps", "save", "savefig", "to_csv", "to_parquet", "to_json",
    "mkdir", "makedirs", "rmtree", "remove", "unlink", "rename", "replace", "scandir",
    "listdir", "walk", "glob", "iterdir", "isfile", "isdir", "getsize", "getmtime",
    "read_csv", "read_parquet", "read_json", "openpyxl_load",
})
QUESTION_ATTRS = frozenset({
    "exists", "is_file", "is_dir", "parent", "parents", "name", "stem", "suffix", "suffixes",
    "parts", "anchor", "as_posix", "resolve", "absolute", "samefile", "is_absolute",
    "endswith", "startswith", "split", "rsplit", "basename", "dirname", "splitdrive",
    "relpath", "normpath", "abspath", "expanduser",
})
COMPOSE_TAILS = frozenset({"join", "truediv"})


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
    return [p for p in e419.corpus()
            if not os.path.basename(p).startswith(SELF_SKIP)]


def _tail(node) -> str:
    """The final name of a dotted expression: `os.path.join` -> join, `p.write_text` -> write_text."""
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


def _is_path_ctor(node) -> bool:
    """`Path(...)`, `pathlib.Path(...)`, `PurePath(...)` -- the left operand of a division."""
    if not isinstance(node, ast.Call):
        return False
    name = _tail(node.func)
    return name.endswith("Path") or name in ("joinpath",)


def _composition_kind(node) -> str:
    if isinstance(node, ast.Call) and _tail(node.func) == "join":
        dotted = _dotted(node.func)
        if dotted.endswith("path.join") or dotted in ("join", "posixpath.join", "ntpath.join"):
            return K_JOIN
        return ""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = node.left
        if _is_path_ctor(left) or (_composition_kind(left) == K_DIV):
            return K_DIV
        if isinstance(left, ast.BinOp) and isinstance(left.op, ast.Div):
            return K_DIV
        return ""
    return ""


def _walk_scope(node, parents: tuple, out: list) -> None:
    """Collect (node, parents) inside one scope, not descending into a nested def/lambda/class."""
    out.append((node, parents))
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        _walk_scope(child, parents + (node,), out)


def _walk_all(node, parents: tuple, out: list) -> None:
    out.append((node, parents))
    for child in ast.iter_child_nodes(node):
        _walk_all(child, parents + (node,), out)


def _scopes(tree) -> list[tuple[str, str, ast.AST, bool]]:
    """(scope_label, scope_kind, body_node, include_nested) for every scope in the file."""
    out: list[tuple[str, str, ast.AST, bool]] = [("", "module", tree, True)]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((node.name, "function", node, True))
    return out


def _inside_nested_scope(parents: tuple, scope_node=None) -> bool:
    """True when the read sits inside a def/lambda other than the scope being followed."""
    for a in parents:
        if a is scope_node:
            continue
        if isinstance(a, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            return True
    return False


def _classify_use(parents: tuple) -> str:
    """How a single read of the bound name is used, judged from its immediate ancestors."""
    if not parents:
        return C_OTHER
    parent = parents[-1]
    if isinstance(parent, ast.Return):
        return C_RETURN
    if isinstance(parent, ast.Dict):
        return C_DICT
    if isinstance(parent, ast.Call):
        if _composition_kind(parent):
            return C_NESTED
        tail = _tail(parent.func)
        if tail in OPEN_RW_TAILS:
            return C_OPEN
        return C_HELPER
    if isinstance(parent, ast.Attribute):
        attr = parent.attr
        grand = parents[-2] if len(parents) > 1 else None
        if isinstance(grand, ast.Call) and grand.func is parent:
            if attr in OPEN_RW_TAILS:
                return C_OPEN
            if attr in QUESTION_ATTRS:
                return C_QUESTION
            return C_HELPER
        if attr in QUESTION_ATTRS:
            return C_QUESTION
        return C_OTHER
    if isinstance(parent, ast.JoinedStr):
        return C_OTHER
    if isinstance(parent, (ast.Subscript, ast.Compare, ast.BoolOp, ast.BinOp)):
        return C_OTHER
    # a nested scope's body: the name is read through a closure, not dropped
    return C_CLOSURE


_USE_RANK = {
    C_OPEN: 0, C_DICT: 1, C_RETURN: 2, C_HELPER: 3, C_CLOSURE: 4, C_QUESTION: 5, C_OTHER: 6,
}


def _name_index(scope_node) -> dict[str, list[tuple]]:
    """Every Name node in the scope, by spelling, with its ancestor chain.

    Built once per scope: the first draft re-walked the whole scope for every composition site,
    which is quadratic on a file with a large module body (17k-line files stalled the scan).
    """
    pairs: list[tuple] = []
    _walk_all(scope_node, (), pairs)
    index: dict[str, list[tuple]] = {}
    for node, parents in pairs:
        if isinstance(node, ast.Name):
            index.setdefault(node.id, []).append((node, parents))
    return index


def _bound_use(index: dict[str, list[tuple]], name: str, assigned_at: int,
               scope_node) -> tuple[str, int, bool]:
    """The strongest read of `name` at or after the assignment, and its read count.

    A read that happens inside a nested def/lambda is a closure capture: the value does leave the
    scope, so it is published as its own class rather than as a consumer or as a drop.
    """
    best = ""
    reads = 0
    rebound = False
    for node, parents in index.get(name, ()):
        if isinstance(node.ctx, ast.Load):
            if getattr(node, "lineno", 0) < assigned_at:
                continue
            reads += 1
            cls = C_CLOSURE if _inside_nested_scope(parents, scope_node) else _classify_use(parents)
            if not best or _USE_RANK.get(cls, 9) < _USE_RANK.get(best, 9):
                best = cls
        elif isinstance(node.ctx, ast.Store) and getattr(node, "lineno", 0) > assigned_at:
            rebound = True
    return best, reads, rebound


def _immediate_class(parents: tuple) -> str:
    """Class for a composition whose value is not bound to a plain name."""
    if not parents:
        return C_UNBOUND
    parent = parents[-1]
    if isinstance(parent, ast.Call):
        if _composition_kind(parent):
            return C_NESTED
        tail = _tail(parent.func)
        return C_AT_OPENER if tail in OPEN_RW_TAILS else C_AT_HELPER
    if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div):
        return C_NESTED
    if isinstance(parent, ast.Return):
        return C_RETURN
    if isinstance(parent, ast.Dict):
        return C_DICT
    if isinstance(parent, ast.Assign) and len(parent.targets) == 1:
        target = parent.targets[0]
        if isinstance(target, ast.Attribute):
            return C_SLOT
        if isinstance(target, ast.Subscript):
            return C_SLOT
        return C_UNBOUND
    if isinstance(parent, (ast.AnnAssign, ast.AugAssign)):
        return C_SLOT if isinstance(parent.target, (ast.Attribute, ast.Subscript)) else C_UNBOUND
    if isinstance(parent, ast.JoinedStr):
        return C_OTHER
    if isinstance(parent, ast.Subscript):
        return C_OTHER
    return C_UNBOUND


def _splitlines_no_ff(source: str) -> list[str]:
    """ast's own splitter: lines keep their terminators, only \\r / \\n split."""
    idx, lines, next_line = 0, [], ""
    while idx < len(source):
        c = source[idx]
        next_line += c
        idx += 1
        if c == "\r" and idx < len(source) and source[idx] == "\n":
            next_line += "\n"
            idx += 1
        if c in "\r\n":
            lines.append(next_line)
            next_line = ""
    if next_line:
        lines.append(next_line)
    return lines


def _segmenter(src: str):
    """ast.get_source_segment, with the source split once instead of per call.

    CPython's helper calls _splitlines_no_ff(source) on every invocation, so a
    scan that asks for one segment per composition site re-splits the whole file
    once per site -- the build spent 16 minutes of CPU on this corpus. The
    slicing (byte-offset columns, first/middle/last line join) is copied from
    ast.get_source_segment so the published `expression` text is unchanged.
    """
    lines = _splitlines_no_ff(src)

    def seg(node) -> str:
        if node is None:
            return ""
        a = getattr(node, "lineno", None)
        b = getattr(node, "end_lineno", None)
        c0 = getattr(node, "col_offset", None)
        c1 = getattr(node, "end_col_offset", None)
        if a is None or b is None or c0 is None or c1 is None:
            return ""
        a -= 1
        b -= 1
        if a < 0 or b >= len(lines) or a > b:
            return ""
        try:
            if a == b:
                return lines[a].encode()[c0:c1].decode()
            first = lines[a].encode()[c0:].decode()
            last = lines[b].encode()[:c1].decode()
            return "".join([first] + lines[a + 1:b] + [last])
        except Exception:  # noqa: BLE001 - source segments are best effort
            return ""

    return seg


def scan_source(rel: str, src: str) -> list[dict]:
    """Every composition site in one source, graded by what its value reaches."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    rows: list[dict] = []
    scopes = _scopes(tree)
    segment = _segmenter(src)
    for label, kind, body, include_nested in scopes:
        pairs: list[tuple] = []
        _walk_scope(body, (), pairs)
        index: dict[str, list[tuple]] | None = None
        for node, parents in pairs:
            if not isinstance(node, (ast.Call, ast.BinOp)):
                continue
            kind_of = _composition_kind(node)
            if not kind_of:
                continue
            # A division inside a division is the same composition, graded once at the outermost.
            if parents and isinstance(parents[-1], ast.BinOp) \
                    and isinstance(parents[-1].op, ast.Div) and _composition_kind(parents[-1]) == K_DIV:
                continue
            consumption = ""
            binding = ""
            rebound = False
            reads = 0
            if parents and isinstance(parents[-1], ast.Assign) and len(parents[-1].targets) == 1 \
                    and isinstance(parents[-1].targets[0], ast.Name) \
                    and parents[-1].value is node:
                binding = parents[-1].targets[0].id
                if index is None:
                    index = _name_index(body)
                consumption, reads, rebound = _bound_use(
                    index, binding, getattr(node, "lineno", 0), body)
                if not consumption:
                    consumption = C_DROPPED
            else:
                consumption = _immediate_class(parents)
            text = segment(node)
            rows.append({
                "file": rel,
                "line": int(getattr(node, "lineno", 1)),
                "col": int(getattr(node, "col_offset", 0)),
                "scope": label or "<module>",
                "kind": kind_of,
                "binding": binding,
                "consumption": consumption,
                "reads": reads,
                "name_rebound_in_scope": bool(rebound),
                "expression": " ".join(text.split())[:MAX_TEXT],
            })
    return rows


def build(cutoff: str | None = None) -> dict:
    cutoff = cutoff or date.today().isoformat()
    names = corpus()
    rows: list[dict] = []
    parsed = 0
    for rel in names:
        try:
            src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        parsed += 1
        rows.extend(scan_source(rel, src))
    rows.sort(key=lambda r: (r["file"], r["line"], r["col"]))
    return face_of(rows, parsed, cutoff)


def _tally(rows: list[dict], key: str, vocab) -> dict:
    out = {v: 0 for v in vocab}
    for r in rows:
        v = r.get(key)
        out[v] = out.get(v, 0) + 1
    return out


def verdict_for(rows: list[dict]) -> str:
    if not rows:
        return V_NONE
    # An unbound site is a composition this reader could not follow -- it is graded as dropped
    # because the corpus cannot show a consumer for it either.
    if any(r.get("consumption") in DROPPED for r in rows):
        return V_SOME
    return V_ALL


def face_of(rows: list[dict], parsed: int, cutoff: str) -> dict:
    by_consumption = _tally(rows, "consumption", CONSUMPTION_VOCAB)
    by_kind = _tally(rows, "kind", KIND_VOCAB)
    scope_kinds: dict[str, int] = {}
    for r in rows:
        key = "module" if r["scope"] == "<module>" else "function"
        scope_kinds[key] = scope_kinds.get(key, 0) + 1
    by_file: dict[str, int] = {}
    for r in rows:
        by_file[r["file"]] = by_file.get(r["file"], 0) + 1
    dropped = sum(by_consumption.get(c, 0) for c in DROPPED)
    reaching = sum(by_consumption.get(c, 0) for c in REACHING)
    e436 = e436_residual(rows)
    summary = {
        "corpus_sources": parsed,
        "composition_sites": len(rows),
        "sites_by_kind": by_kind,
        "sites_by_consumption": by_consumption,
        "sites_by_scope_kind": scope_kinds,
        "files_with_sites": len(by_file),
        "sites_by_file": dict(sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))),
        "sites_that_reach_a_consumer": reaching,
        "dropped_sites": dropped,
        "dropped_share": (round(dropped / len(rows), 4) if rows else 0.0),
        "question_only_sites": by_consumption.get(C_QUESTION, 0),
        "closure_only_sites": by_consumption.get(C_CLOSURE, 0),
        "slot_sites": by_consumption.get(C_SLOT, 0),
        "nested_composition_sites": by_consumption.get(C_NESTED, 0),
        "sites_whose_bound_name_is_rebound": sum(1 for r in rows if r["name_rebound_in_scope"]),
        # a composition that sits directly in a return / dict literal reaches a consumer
        # without any name being bound, so it is counted here rather than left invisible
        "sites_reaching_without_a_bound_name": sum(
            1 for r in rows if not r.get("binding")
            and r["consumption"] in (C_DICT, C_RETURN)),
        "compositions_that_open_themselves_are_excluded": by_consumption.get(C_AT_OPENER, 0),
        "e436_residual": e436,
    }
    return {
        "study": "E442_which_path_composition_is_never_consumed",
        "card": CARD,
        "title": "every path composition in the corpus, graded by whether its value reaches a "
                 "consumer from the scope that composed it",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff,
        "verdict": verdict_for(rows),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "the follow is one name wide: `p = join(...)` then `q = p` then open(q) reads as "
            "`flows_into_another_call`-free (p is only assigned to q, classed as a non-consuming "
            "use), so aliasing through a second name is not followed and a dropped site can be a "
            "missed consumer rather than a missing one",
            "the read test is by name inside the scope, not by position: a read that appears "
            "before the assignment on the same name (a loop variable, a previous binding) counts "
            "and is disclosed by `name_rebound_in_scope` instead of being resolved",
            "a composition is recognised by the dotted tail `path.join` (or a bare `join`) and by "
            "a *Path / *path constructor on the left of a division; `obj.join(a, b)` on some other "
            "receiver is not in the population, so this face bounds `path.join` sites only",
            "Path division is recognised when the left operand is a *Path constructor or another "
            "division; `p / 'x'` where p is a name bound earlier is not in this population",
            "scope is the nearest def/class-free body; a name read only inside a nested def counts "
            "as a closure capture and is published in its own class rather than as a consumer",
            "static only: nothing is executed, so a path handed to a function that opens it "
            "somewhere else is `flows_into_another_call`, not `consumed`",
        ],
    }


def e436_residual(rows: list[dict]) -> dict:
    """Grade the sites E436 named and never followed (the card's origin)."""
    try:
        face = _load(os.path.join(OUTDIR, "doublejoin_latest.json"))
    except (OSError, ValueError):
        return {"source": "doublejoin_latest.json", "available": False}
    named: list[str] = []
    for block in face.get("targets") or []:
        for site in block.get("sites") or []:
            if isinstance(site, str) and ":" in site:
                named.append(site)
    for key in ("read_sites", "write_sites"):
        for site in face.get(key) or []:
            if isinstance(site, dict) and site.get("file"):
                named.append("%s:%s" % (site["file"], site.get("line")))
    uniq = sorted(set(named))
    index: dict[tuple[str, int], dict] = {}
    for r in rows:
        index[(r["file"], r["line"])] = r
    graded: dict[str, str] = {}
    unresolved: list[str] = []
    for site in uniq:
        f, _, ln = site.rpartition(":")
        try:
            key = (f.replace("\\", "/"), int(ln))
        except ValueError:
            unresolved.append(site)
            continue
        row = index.get(key)
        if row is None:
            unresolved.append(site)
        else:
            graded[site] = row["consumption"]
    by_class: dict[str, int] = {}
    for cls in graded.values():
        by_class[cls] = by_class.get(cls, 0) + 1
    return {
        "source": "doublejoin_latest.json",
        "available": True,
        "e436_sites_named": len(uniq),
        "graded_here": len(graded),
        "unresolved": unresolved,
        "by_consumption": dict(sorted(by_class.items())),
        "dropped_among_them": sum(v for k, v in by_class.items() if k in DROPPED),
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))
    _dump(path, face)
    _dump(dated, face)
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not isinstance(rows, list):
        return ["rows is not a list"]
    by_consumption = {c: 0 for c in CONSUMPTION_VOCAB}
    by_kind = {k: 0 for k in KIND_VOCAB}
    scope_kinds = {"module": 0, "function": 0}
    by_file: dict[str, int] = {}
    for r in rows:
        cls = r.get("consumption")
        if cls not in CONSUMPTION_VOCAB:
            problems.append("%s:%s consumption outside the vocabulary" % (r.get("file"), r.get("line")))
            continue
        if r.get("kind") not in KIND_VOCAB:
            problems.append("%s:%s kind outside the vocabulary" % (r.get("file"), r.get("line")))
            continue
        by_consumption[cls] += 1
        by_kind[r["kind"]] += 1
        scope_kinds["module" if r.get("scope") == "<module>" else "function"] += 1
        by_file[r["file"]] = by_file.get(r["file"], 0) + 1
        if cls == C_DROPPED and r.get("reads"):
            problems.append("%s:%s is dropped but carries %s read(s)"
                            % (r["file"], r["line"], r["reads"]))
        if cls in (C_OPEN, C_HELPER, C_CLOSURE) and not r.get("binding"):
            problems.append("%s:%s flows out of a name it never bound" % (r["file"], r["line"]))
        if cls in (C_DICT, C_RETURN) and not r.get("binding") and r.get("reads"):
            problems.append("%s:%s reaches a payload directly but carries reads"
                            % (r["file"], r["line"]))
    if by_consumption != (s.get("sites_by_consumption") or {}):
        problems.append("sites_by_consumption does not re-derive from the rows")
    if by_kind != (s.get("sites_by_kind") or {}):
        problems.append("sites_by_kind does not re-derive from the rows")
    if scope_kinds != (s.get("sites_by_scope_kind") or {}):
        problems.append("sites_by_scope_kind does not re-derive from the rows")
    if dict(sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))) != (s.get("sites_by_file") or {}):
        problems.append("sites_by_file does not re-derive from the rows")
    if sum(by_consumption.values()) != (s.get("composition_sites") or 0):
        problems.append("the consumption tally does not close over the population")
    if len(rows) != (s.get("composition_sites") or 0):
        problems.append("composition_sites does not equal the number of rows")
    dropped = sum(by_consumption.get(c, 0) for c in DROPPED)
    if dropped != (s.get("dropped_sites") or 0):
        problems.append("dropped_sites does not re-derive")
    if sum(by_consumption.get(c, 0) for c in REACHING) != (s.get("sites_that_reach_a_consumer") or 0):
        problems.append("sites_that_reach_a_consumer does not re-derive")
    direct = sum(1 for r in rows if not r.get("binding")
                 and r.get("consumption") in (C_DICT, C_RETURN))
    if direct != (s.get("sites_reaching_without_a_bound_name") or 0):
        problems.append("sites_reaching_without_a_bound_name does not re-derive")
    if verdict_for(rows) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the published rows")
    res = s.get("e436_residual") or {}
    if res.get("available"):
        if res.get("graded_here", 0) + len(res.get("unresolved") or []) != res.get("e436_sites_named", 0):
            problems.append("the E436 residue does not close over the sites it names")
        by_class = res.get("by_consumption") or {}
        if sum(by_class.values()) != res.get("graded_here", 0):
            problems.append("the E436 residue classes do not close over the graded sites")
        if sum(v for k, v in by_class.items() if k in DROPPED) != res.get("dropped_among_them", 0):
            problems.append("the E436 dropped count does not re-derive")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    for key in ("composition_sites", "sites_by_consumption", "sites_by_kind",
                "dropped_sites", "sites_that_reach_a_consumer"):
        if live["summary"].get(key) != face["summary"].get(key):
            problems.append("live %s differs from the published face" % key)
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    def classes(src: str) -> dict:
        rows = scan_source("scripts/fixture.py", src)
        out: dict[str, str] = {}
        for r in rows:
            out[r["binding"] or ("@%d" % r["line"])] = r["consumption"]
        return out

    # 1-2: a join bound and handed straight to open
    c = classes("import os\np = os.path.join('a', 'b')\nopen(p)\n")
    check("opener_read_is_consumption", c.get("p") == C_OPEN and len(c) == 1)
    c = classes("import os\np = os.path.join('a', 'b')\nq = open(p)\nq.close()\n")
    check("opener_as_argument_still_counts", c.get("p") == C_OPEN)
    # 3: bound and never read -> dropped, with zero reads
    rows = scan_source("scripts/fixture.py", "import os\np = os.path.join('a', 'b')\n")
    check("unused_binding_is_dropped",
          len(rows) == 1 and rows[0]["consumption"] == C_DROPPED and rows[0]["reads"] == 0)
    # 4: dict literal is a payload, not a drop
    c = classes("import os\np = os.path.join('a', 'b')\nd = {'path': p}\n")
    check("dict_literal_is_a_payload", c.get("p") == C_DICT)
    # 5: return
    c = classes("import os\ndef f():\n    p = os.path.join('a', 'b')\n    return p\n")
    check("return_is_consumption", c.get("p") == C_RETURN)
    # 6: exists() is a question about the path, not a consumer
    c = classes("import os\np = os.path.join('a', 'b')\nif p.exists():\n    pass\n")
    check("exists_is_only_a_question", c.get("p") == C_QUESTION)
    # 7: handed to a helper
    c = classes("import os\np = os.path.join('a', 'b')\nprint(p)\n")
    check("helper_call_is_classed_as_a_call", c.get("p") == C_HELPER)
    # 8: the join consumed at the call site
    c = classes("import os\nopen(os.path.join('a', 'b'))\n")
    check("call_site_opener", list(c.values()) == [C_AT_OPENER])
    # 9: the join handed to a non-opener
    c = classes("import os\nprint(os.path.join('a', 'b'))\n")
    check("call_site_helper", list(c.values()) == [C_AT_HELPER])
    # 10: part of a larger composition
    rows = scan_source("scripts/fixture.py",
                       "import os\nos.path.join('a', os.path.join('b', 'c'))\n")
    check("nested_join_is_one_class",
          sorted(r["consumption"] for r in rows) == sorted([C_NESTED, C_UNBOUND]))
    # 11: Path division
    c = classes("from pathlib import Path\np = Path('a') / 'b'\nopen(p)\n")
    check("path_division_is_a_composition", c.get("p") == C_OPEN and len(c) == 1)
    # 12: stored into a slot directly
    c = classes("import os\ncfg = {}\ncfg['p'] = os.path.join('a', 'b')\n")
    check("slot_store_is_its_own_class", list(c.values()) == [C_SLOT])
    # 13: a bare expression statement cannot be followed
    c = classes("import os\nos.path.join('a', 'b')\n")
    check("bare_statement_is_unbound", list(c.values()) == [C_UNBOUND])
    # 14: closure capture is not a drop
    c = classes("import os\np = os.path.join('a', 'b')\ndef g():\n    return open(p)\n")
    check("closure_capture_is_not_a_drop", c.get("p") == C_CLOSURE)
    # 15: a name rebound after the assignment is flagged
    rows = scan_source("scripts/fixture.py",
                       "import os\np = os.path.join('a', 'b')\np = 'other'\nopen(p)\n")
    check("rebinding_is_flagged", len(rows) == 1 and rows[0]["name_rebound_in_scope"] is True)
    # 16: verify the verdict across the three shapes
    check("verdict_none", verdict_for([]) == V_NONE)
    check("verdict_all_reached",
          verdict_for([{"consumption": C_OPEN, "kind": K_JOIN}]) == V_ALL)
    check("verdict_some_dropped",
          verdict_for([{"consumption": C_DROPPED, "kind": K_JOIN}]) == V_SOME)
    # 17-19: the tally refuses a doctored face
    face = face_of([{"file": "scripts/a.py", "line": 1, "col": 0, "scope": "<module>",
                     "kind": K_JOIN, "binding": "p", "consumption": C_DROPPED, "reads": 0,
                     "name_rebound_in_scope": False, "expression": "x"},
                    {"file": "scripts/a.py", "line": 2, "col": 0, "scope": "f",
                     "kind": K_DIV, "binding": "q", "consumption": C_OPEN, "reads": 1,
                     "name_rebound_in_scope": False, "expression": "y"}], 3, "2026-11-05")
    check("face_clean", tally_problems(face) == [])
    bad = json.loads(json.dumps(face))
    bad["summary"]["dropped_sites"] = 0
    check("tally_catches_a_wrong_drop_count", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(face))
    bad2["verdict"] = V_ALL
    check("tally_catches_a_carried_verdict", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(face))
    bad3["rows"][0]["reads"] = 2
    check("tally_catches_a_drop_that_claims_a_read", tally_problems(bad3) != [])
    bad4 = json.loads(json.dumps(face))
    bad4["summary"]["sites_by_kind"][K_DIV] = 0
    check("tally_catches_a_shifted_kind", tally_problems(bad4) != [])
    # 20: syntax errors never crash the scan
    check("unparseable_source_is_empty", scan_source("scripts/broken.py", "def (:\n") == [])
    # 21: the corpus excludes this study's own files
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
        print(json.dumps(s["sites_by_consumption"], ensure_ascii=False))
        print("sites %d over %d sources (%d files): reaching %d, dropped %d (%s)"
              % (s["composition_sites"], s["corpus_sources"], s["files_with_sites"],
                 s["sites_that_reach_a_consumer"], s["dropped_sites"], s["dropped_share"]))
        res = s.get("e436_residual") or {}
        if res.get("available"):
            print("E436 residue: %d named, %d graded here, %d dropped"
                  % (res["e436_sites_named"], res["graded_here"], res["dropped_among_them"]))
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
        face = _load(os.path.join(OUTDIR, FACE_NAME))
        problems = tally_problems(face)
        if face.get("verdict") not in VERDICT_VOCAB:
            problems.append("the published verdict is not in the study's vocabulary")
        print("check problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 1 if problems else 0
    print("usage: run|verify|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))