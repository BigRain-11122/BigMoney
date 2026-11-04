"""E429: follow the directory a face name is composed with, one hop further than E419 did.

E419 asked, for each face with no readable date, "which in-repo function writes this face".
Its attribution is one-hop and literal: a write target must spell the basename, in the face's
own directory, inside the same function.  It left 3 of its 9 rows graded
``no_writer_in_the_tree`` and said in its own method limits that a face composed from a
variable and written by a shared helper is out of reach.

That is not a rare shape.  Three of the three rows are composed exactly that way:

  * ``results/etf_book_production/CARD.md``  -- ``open(os.path.join(OUT_DIR, "CARD.md"), "w")``
    and ``OUT_DIR`` is a module constant whose value spells the directory;
  * ``docs/futures_lane/TSMOM-%s.md``        -- ``page = os.path.join(DOC_DIR, "TSMOM-%s.md" % d)``
    then ``open(page, "w")``, and ``DOC_DIR`` spells ``docs/futures_lane``;
  * ``results/state_tilt/AGGATT-%s.json``    -- the name is built inside ``_write(face, outdir)``
    and the *directory* arrives as a parameter, supplied at the call sites.

So this study asks one question: how many of those rows become writers once the directory is
followed to the site that supplies it.  Two hop kinds are counted, both mechanically:

  * ``constant`` -- the path expression is expanded through module and function constants up to
    three substitutions, and the expanded text names both the stem and the directory token;
  * ``caller``   -- the write target's directory is a parameter of the helper, so every call to
    that helper in the corpus is resolved with the caller's own constants and graded on whether
    it supplies the face's directory.

A row is only called a writer when the site it lands on actually opens for writing (``open`` in
a write mode, ``Path.write_text``/``write_bytes``, or ``to_csv``/``to_parquet``/``savefig`` with
a path argument).  A function that names the face and opens it for READING is not a writer --
the first draft of this study made ``etf_book_production.py:1050`` the author of CARD.md because
it *reads* a CARD.md out of a temp directory.

The corpus half of the card ("the fraction of the corpus that a two-hop walk would reach") is
measured rather than estimated: every write site's path expression is split into
literal-only / parameter-derived / both, and every parameter-derived site is offered to the
call index.  Sites whose helper name resolves to no call site in the corpus are published as
unresolved rather than folded into either side.

Usage:
    python scripts/e429_two_hop_writer.py run|verify|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

import e419_unstampable as e419

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
E419_FACE = os.path.join(ST, "unstampable_latest.json")
OUTDIR = ST

E419_MISSING = e419.W_MISSING

W_DATE = "writer_with_a_date"
W_NODATE = "writer_without_a_date"
W_HELPER = "helper_declared_but_no_caller_supplies_the_directory"
W_STILL = "still_no_writer_in_the_tree"
CLASS_VOCAB = (W_DATE, W_NODATE, W_HELPER, W_STILL)

HOP_CONST = "constant"
HOP_CALLER = "caller"
HOP_NONE = "none"

V_ALL = "every_no_writer_row_became_a_writer_once_the_directory_was_followed"
V_SOME = "some_no_writer_rows_became_writers_once_the_directory_was_followed"
V_NONE = "no_no_writer_row_became_a_writer_even_two_hops_away"
V_EMPTY = "no_no_writer_row_to_test"
VERDICT_VOCAB = (V_ALL, V_SOME, V_NONE, V_EMPTY)

# Counts that move when a .py file appears or is deleted.  Declared in the face and checked by
# the producer, never equality-gated by the leg (scripts/population_keys.py, r1441 law).
POPULATION_KEYS = ("corpus_sources", "write_sites")

# The write-path instrument: only calls whose FIRST argument (or receiver, for the Path family)
# is the persisted path.  json.dump is deliberately absent -- its second argument is an open
# handle, and the `open()` that produced it is counted in the same function.
PATH_WRITE_ATTRS = {"write_text", "write_bytes", "to_csv", "to_parquet", "savefig",
                    "write_parquet"}
MAX_TEXT = 4000
TOKEN = re.compile(r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')|([A-Za-z_][A-Za-z0-9_]*)")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list[str]:
    """E419's census scope, minus this study's own files (the self-inclusion law, E180/E207)."""
    skip = ("e429", "run_e429")
    return [p for p in e419.corpus() if not os.path.basename(p).startswith(skip)]


# ---------------------------------------------------------------- expression environments

def _worth_binding(text: str, node: ast.AST) -> bool:
    """Is this expression a path-ish binding worth following?

    A literal is the obvious case, but `outdir = outdir or OUTDIR` and `p = ROOT_DIR` are the
    shapes a default argument and an alias take -- both carry no quote of their own and were
    invisible to a literal-only rule (the first draft then graded a helper that *does* receive
    its directory as "no caller supplies it").
    """
    if not text:
        return False
    if '"' in text or "'" in text:
        return True
    return isinstance(node, (ast.Name, ast.Attribute, ast.BoolOp, ast.IfExp, ast.JoinedStr,
                             ast.Subscript))


def seg(lines: list[str], node: ast.AST) -> str:
    """Exact source text of a node, sliced off pre-split lines.

    e419 used whole-line slices, which is enough for a substring search but wrong for a VALUE:
    `name = "AGG-%s.json" % face` sliced as a line carries its own assignment back into every
    substitution (the first draft of this study printed `outdir, name = 'AGG-%s.json' % face`
    inside the resolved path).  Columns are exact and the slice costs nothing per node.
    """
    start = getattr(node, "lineno", None)
    end = getattr(node, "end_lineno", None)
    start_c = getattr(node, "col_offset", 0) or 0
    end_c = getattr(node, "end_col_offset", None)
    if start is None or end is None or end_c is None or start - 1 >= len(lines):
        return ""
    if start == end:
        return lines[start - 1][start_c:end_c]
    parts = [lines[start - 1][start_c:]]
    parts.extend(lines[start:end - 1])
    parts.append(lines[end - 1][:end_c])
    return "\n".join(parts)


def module_env(tree: ast.Module, lines: list[str]) -> dict[str, str]:
    """Module-level names bound to an expression that spells something."""
    env: dict[str, str] = {}
    for node in tree.body:
        targets: list[ast.expr] = []
        value = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None:
            continue
        text = seg(lines, value)
        if not _worth_binding(text, value):
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                env[t.id] = text
    return env


def function_env(fn: ast.AST, lines: list[str]) -> dict[str, str]:
    """Function-local names bound to an expression that spells something."""
    env: dict[str, str] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            text = seg(lines, node.value)
            if _worth_binding(text, node.value):
                env[node.targets[0].id] = text
    return env


def resolve(text: str, envs: list[dict[str, str]], hops: int = 3) -> str:
    """Substitute bound names, up to `hops` rounds, leaving quoted strings untouched.

    A name bound to an expression that mentions itself (`outdir = outdir or OUTDIR`) is allowed:
    each round is bounded by `hops` and by MAX_TEXT, and the self-reference is exactly the shape
    a caller's default argument takes.
    """
    cur = text or ""
    for _ in range(hops):
        if len(cur) > MAX_TEXT:
            break

        def rep(m: re.Match) -> str:
            if m.group(1) is not None:          # a quoted string is data, not a reference
                return m.group(1)
            tok = m.group(2)
            for env in envs:
                val = env.get(tok)
                if val is not None and val != tok:
                    return val
            return tok

        nxt = TOKEN.sub(rep, cur)
        if nxt == cur:
            break
        cur = nxt
    return cur


# ---------------------------------------------------------------- write sites

class Site:
    """One function that opens a path for writing, with the material needed to place it."""

    def __init__(self, path: str, fn: ast.AST, line: int, call_name: str,
                 params: list[str], envs: list[dict[str, str]],
                 paths: list[tuple[str, ast.AST]], keys: set[str],
                 date_holders: list[str], date_calls: list[str], segment: str):
        self.path = path
        self.func = fn.name
        self.line = line
        self.call_name = call_name
        self.params = params
        self.envs = envs
        self.paths = paths
        self.keys = keys
        self.date_holders = date_holders
        self.date_calls = date_calls
        self.segment = segment

    def resolved_paths(self) -> list[str]:
        return [resolve(t, self.envs) for t, _ in self.paths]

    def names_in_path(self) -> set[str]:
        out: set[str] = set()
        for _, node in self.paths:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    out.add(sub.id)
        return out

    def name_encodes_a_date(self, base: str) -> bool:
        """Is the face name composed with a date-named variable?

        `name = "AGGATT-%s.json" % cutoff` is a face whose *name* carries the panel date while
        the payload dict carries none -- a different fact from "the writer holds no date", and
        one a payload-key census cannot see.
        """
        chunks = [t for t, _ in self.paths if base in t]
        chunks += [v for v in self.envs[0].values() if base in v]
        for text in chunks:
            for tok in TOKEN.findall(text):
                ident = tok[1]
                if ident and e419.is_date_name(ident):
                    return True
        return False

    def parameter_directories(self) -> list[str]:
        return [p for p in self.params if p in self.names_in_path()]

    def spells_a_literal(self) -> bool:
        return any('"' in t or "'" in t for t, _ in self.paths)

    def as_row(self) -> dict:
        return {
            "file": self.path,
            "function": self.func,
            "line": self.line,
            "write_call": self.call_name,
            "payload_keys_with_a_date": sorted(k for k in self.keys if k in e419.STAMP_KEYS),
            "date_variables_in_scope": self.date_holders[:6],
            "date_calls_in_scope": self.date_calls,
        }


def _path_expr(call: ast.Call) -> ast.expr | None:
    """The expression that names the persisted path, or None when this is not a path write."""
    name = e419._call_name(call)
    if name == "open":
        if e419._is_write_call(call) and call.args:
            return call.args[0]
        return None
    if name in ("write_text", "write_bytes"):
        return call.func.value if isinstance(call.func, ast.Attribute) else None
    if name in PATH_WRITE_ATTRS:
        if call.args:
            return call.args[0]
        for kw in call.keywords:
            if kw.arg in ("path_or_buf", "path", "fname", "excel_writer"):
                return kw.value
    return None


def scan_file(path: str, src: str) -> list[Site]:
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    lines = src.splitlines()
    menv = module_env(tree, lines)
    sites: list[Site] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        paths: list[tuple[str, ast.AST]] = []
        call_names: list[str] = []
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            expr = _path_expr(node)
            if expr is None:
                continue
            text = seg(lines, expr)
            if not text:
                continue
            paths.append((text, expr))
            call_names.append(e419._call_name(node))
        if not paths:
            continue
        params = [a.arg for a in list(fn.args.posonlyargs) + list(fn.args.args) + list(fn.args.kwonlyargs)]
        envs = [function_env(fn, lines), menv, dict(menv, **function_env(fn, lines))]
        keys: set[str] = set()
        dumped: set[str] = set()
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            name = e419._call_name(node)
            if name in ("dump", "dumps") and node.args:
                first = node.args[0]
                if isinstance(first, ast.Name):
                    dumped.add(first.id)
                else:
                    keys |= e419._dict_keys(first)
            elif name == "write" and isinstance(node.func, ast.Attribute):
                for arg in node.args:            # fh.write(json.dumps(payload))
                    keys |= e419._dict_keys(arg)
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in dumped and isinstance(node.value, ast.Dict):
                        keys |= e419._dict_keys(node.value)
                    elif isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) \
                            and t.value.id in dumped \
                            and isinstance(t.slice, ast.Constant) \
                            and isinstance(t.slice.value, str):
                        keys.add(t.slice.value)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "setdefault" and isinstance(node.func.value, ast.Name) \
                    and node.func.value.id in dumped and node.args \
                    and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                keys.add(node.args[0].value)
        holders: list[str] = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Name) and e419.is_date_name(node.id):
                holders.append(node.id)
            elif isinstance(node, ast.Call):
                name = e419._call_name(node)
                if name and e419.is_date_name(name) and name not in ("open", "load", "dump"):
                    holders.append(name)
        fn_text = e419._seg(lines, fn)
        sites.append(Site(path, fn, fn.lineno, "+".join(sorted(set(call_names))), params,
                          envs, paths, keys, sorted(set(holders)),
                          sorted(set(e419.DATE_CALL.findall(fn_text))), fn_text))
    return sites


def scan_corpus(names: list[str]) -> tuple[dict[str, list[Site]], int]:
    """Write sites per source; the second value is the number of sources parsed."""
    sites: dict[str, list[Site]] = {}
    parsed = 0
    for rel in names:
        try:
            src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        parsed += 1
        found = scan_file(rel, src)
        if found:
            sites[rel] = found
    return sites, parsed


# ---------------------------------------------------------------- call sites

def main_call_index(wanted: set[str], sources: list[str]) -> dict[str, list[dict]]:
    """Tree-wide call sites, filed under the callee name (via _iter_calls)."""
    idx: dict[str, list[dict]] = {n: [] for n in wanted}
    if not wanted:
        return idx
    needles = tuple(n + "(" for n in wanted)
    for rel in sources:
        try:
            src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not any(nd in src for nd in needles):
            continue
        try:
            tree = ast.parse(src)
        except (SyntaxError, ValueError):
            continue
        lines = src.splitlines()
        menv = module_env(tree, lines)
        for call, owner in _iter_calls(tree):
            name = e419._call_name(call)
            if name not in idx:
                continue
            fenv = function_env(owner, lines) if owner is not None else {}
            idx[name].append({
                "file": rel,
                "caller": getattr(owner, "name", "<module>"),
                "line": call.lineno,
                "args": [seg(lines, a) for a in call.args],
                "kwargs": {kw.arg: seg(lines, kw.value) for kw in call.keywords if kw.arg},
                "env": dict(menv, **fenv),
            })
    return idx


def _iter_calls(tree: ast.Module):
    """(call, enclosing function or None) for every call in the module."""
    stack: list[tuple[ast.AST, ast.AST | None]] = [(tree, None)]
    while stack:
        node, owner = stack.pop()
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Call):
                yield child, owner
            nxt_owner = child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else owner
            stack.append((child, nxt_owner))


def resolve_call_argument(call_row: dict, param: str, params: list[str]) -> str:
    """The text a call passes for `param`, expanded through the caller's own constants."""
    text = ""
    if param in call_row["kwargs"]:
        text = call_row["kwargs"][param] or ""
    else:
        try:
            i = params.index(param)
        except ValueError:
            return ""
        if i < len(call_row["args"]):
            text = call_row["args"][i] or ""
    return resolve(text, [call_row["env"]], hops=3)


# ---------------------------------------------------------------- face attribution

def attribute(face: str, base: str, dir_tok: str | None, sites: dict[str, list[Site]],
              index: dict[str, list[dict]]) -> dict:
    """Follow the directory one hop (constant or caller) and grade what lands there."""
    candidates: list[Site] = []
    for rel, found in sites.items():
        for s in found:
            if base not in s.segment:
                continue
            if e419.FIXTURE_HINT.search(rel) or e419.FIXTURE_HINT.search(" ".join(s.resolved_paths())):
                continue
            candidates.append(s)

    def grade(s: Site, base: str) -> dict:
        carries = bool([k for k in s.keys if k in e419.STAMP_KEYS])
        holds = bool(s.date_holders or s.date_calls)
        row = s.as_row()
        return {
            "opener": bool(s.call_name),
            "write_call": s.call_name,
            "position": {"file": s.path, "function": s.func, "line": s.line},
            "writer": row,
            "date_basis": {"payload_keys_with_a_date": row["payload_keys_with_a_date"],
                           "date_variables_in_scope": row["date_variables_in_scope"],
                           "date_calls_in_scope": row["date_calls_in_scope"],
                           "date_in_the_composed_name": s.name_encodes_a_date(base)},
            "classification": W_DATE if (carries and holds) else W_NODATE,
        }

    constant_hits: list[dict] = []
    for s in candidates:
        for text in s.resolved_paths():
            if base not in text:
                continue
            if dir_tok and dir_tok not in text:
                continue
            constant_hits.append({"site": s, "resolved_path": text})
    if constant_hits:
        constant_hits.sort(key=lambda h: (not bool([k for k in h["site"].keys
                                                    if k in e419.STAMP_KEYS]),
                                          e419._one_off(h["site"].path),
                                          h["site"].path, h["site"].line))
        hit = constant_hits[0]
        out = grade(hit["site"], base)
        out.update({"hop_kind": HOP_CONST, "hops_followed": 2,
                    "resolved_path": hit["resolved_path"][:300],
                    "supplied_at": [{"file": hit["site"].path,
                                     "function": hit["site"].func,
                                     "line": hit["site"].line,
                                     "argument": "(module or local constant)"}],
                    "constant_hits": len(constant_hits)})
        return out

    caller_hits: list[dict] = []
    helper_sites: list[Site] = []
    for s in candidates:
        dirs = s.parameter_directories()
        if not dirs:
            continue
        helper_sites.append(s)
        for param in dirs:
            for call_row in index.get(s.func) or []:
                arg = resolve_call_argument(call_row, param, s.params)
                if not arg:
                    continue
                if dir_tok and dir_tok not in arg:
                    continue
                if base in arg:      # the caller spells the whole path, not the directory
                    continue
                caller_hits.append({"site": s, "param": param, "call": call_row, "arg": arg})
    if caller_hits:
        caller_hits.sort(key=lambda h: (not bool([k for k in h["site"].keys
                                                  if k in e419.STAMP_KEYS]),
                                        e419._one_off(h["site"].path),
                                        h["site"].path, h["site"].line))
        hit = caller_hits[0]
        out = grade(hit["site"], base)
        out.update({"hop_kind": HOP_CALLER, "hops_followed": 2,
                    "parameter": hit["param"],
                    "resolved_path": hit["arg"][:300],
                    "supplied_at": [{"file": c["call"]["file"], "function": c["call"]["caller"],
                                     "line": c["call"]["line"],
                                     "argument": c["arg"][:200]}
                                    for c in caller_hits[:4]],
                    "caller_hits": len(caller_hits)})
        return out

    if helper_sites:
        return {"classification": W_HELPER, "hop_kind": HOP_NONE, "hops_followed": 1,
                "opener": True,
                "write_call": helper_sites[0].call_name,
                "position": {"file": helper_sites[0].path,
                             "function": helper_sites[0].func,
                             "line": helper_sites[0].line},
                "helper_takes_the_directory_as_a_parameter":
                    sorted({p for s in helper_sites for p in s.parameter_directories()}),
                "callers_that_supply_the_directory": 0,
                "writer": None,
                "date_basis": None,
                "resolved_path": None,
                "supplied_at": []}
    return {"classification": W_STILL, "hop_kind": HOP_NONE, "hops_followed": 0,
            "opener": False, "write_call": None, "position": None, "writer": None,
            "date_basis": None, "resolved_path": None, "supplied_at": [],
            "candidate_helpers": len(candidates)}


def build(cutoff: str | None = None) -> dict:
    e419_face = _load(E419_FACE)
    cut = cutoff or e419_face["evidence_cutoff"]
    missing = [r for r in e419_face["rows"] if r["classification"] == E419_MISSING]
    sources = corpus()
    sites, parsed = scan_corpus(sources)

    # Names the two-hop walk needs: any site whose path is a directory parameter.
    wanted: set[str] = set()
    for found in sites.values():
        for s in found:
            if s.parameter_directories() and not s.spells_a_literal():
                wanted.add(s.func)
    index = main_call_index(wanted, sources)

    rows = []
    for r in missing:
        base, dir_tok, template = e419.name_pattern(r["face"])
        row = attribute(r["face"], base, dir_tok, sites, index)
        row.update({
            "face": r["face"],
            "name_token": base,
            "directory_token": dir_tok,
            "template": template,
            "one_hop_classification": r["classification"],
            "one_hop_weaker_sites": r.get("weaker_sites_not_counted_as_writers"),
        })
        rows.append(row)
    rows.sort(key=lambda x: (x["classification"], x["face"]))

    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["classification"]] = by_class.get(r["classification"], 0) + 1
    moved = by_class.get(W_DATE, 0) + by_class.get(W_NODATE, 0)

    # Corpus half: which write sites a literal-name census can see at all.
    literal = parameter = both = neither = 0
    param_sites: list[Site] = []
    for found in sites.values():
        for s in found:
            lit = s.spells_a_literal()
            par = bool(s.parameter_directories())
            if lit and par:
                both += 1
            elif lit:
                literal += 1
            elif par:
                parameter += 1
            else:
                neither += 1
            if par:
                param_sites.append(s)

    neither_sites = [s for found in sites.values() for s in found
                     if not s.spells_a_literal() and not s.parameter_directories()]
    neither_by_constant = sum(
        1 for s in neither_sites
        if any('"' in t for t in s.resolved_paths()))

    resolved_literal = resolved_constant = unresolved = 0
    for s in param_sites:
        supplied = []
        for param in s.parameter_directories():
            for call_row in index.get(s.func) or []:
                arg = resolve_call_argument(call_row, param, s.params)
                if arg:
                    supplied.append(arg)
        if not supplied:
            unresolved += 1
        elif any('"' in a or "'" in a for a in supplied):
            resolved_literal += 1
        else:
            resolved_constant += 1

    total_sites = literal + parameter + both + neither
    summary = {
        "faces_in_population": len(rows),
        "by_class": by_class,
        "rows_that_became_writers": moved,
        "rows_with_a_date": by_class.get(W_DATE, 0),
        "rows_without_a_date": by_class.get(W_NODATE, 0),
        "rows_whose_name_encodes_a_date": sum(
            1 for r in rows
            if (r.get("date_basis") or {}).get("date_in_the_composed_name")),
        "corpus_sources": parsed,
        "write_sites": total_sites,
        "corpus": {
            "path_spells_a_literal_only": literal,
            "path_is_parameter_derived_only": parameter,
            "literal_and_parameter": both,
            "neither": neither,
            "literal_visible_share": round((literal + both) / total_sites, 4) if total_sites else 0.0,
            "neither_resolved_by_a_constant_hop": neither_by_constant,
            "visible_after_a_constant_hop": literal + both + neither_by_constant,
            "still_needs_the_caller_hop": total_sites - (literal + both + neither_by_constant),
        },
        "two_hop_reach": {
            "parameter_derived_sites": len(param_sites),
            "caller_supplies_a_literal_directory": resolved_literal,
            "caller_supplies_a_constant_directory": resolved_constant,
            "no_caller_found_in_the_corpus": unresolved,
            "helper_names_resolved": len(wanted),
        },
    }

    if not rows:
        verdict = V_EMPTY
    elif moved == len(rows):
        verdict = V_ALL
    elif moved:
        verdict = V_SOME
    else:
        verdict = V_NONE
    return {
        "study": "E429_which_no_writer_face_is_composed_by_a_helper_the_census_cannot_see",
        "card": "E429-WHICH-NO-WRITER-FACE-IS-COMPOSED-BY-A-HELPER-THE-CENSUS-CANNOT-SEE",
        "title": "follow the directory of every no-writer face one hop further and bill the "
                 "class movement, with the corpus share a two-hop walk reaches",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict,
        "class_vocab": list(CLASS_VOCAB),
        "hop_vocab": [HOP_CONST, HOP_CALLER, HOP_NONE],
        "population_keys": list(POPULATION_KEYS),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "a writer is a function whose path argument is the persisted path: open() in a write "
            "mode, Path.write_text/write_bytes, or to_csv/to_parquet/savefig with a path; a "
            "function that writes through a handle opened elsewhere is invisible (json.dump is "
            "counted through its open)",
            "the caller hop is name-based: a helper name shared by two files in the tree admits "
            "a foreign call site, so a caller hit is a place the directory could come from, not "
            "proof of which call produced the face on disk",
            "constant expansion stops after three substitutions and 4,000 characters; a name "
            "built at runtime (a date-formatted directory, an env var) is not resolved",
            "date_in_the_composed_name reads the writer's own assignment for the stem, so a "
            "name assembled from a loop variable over a tuple of names is not seen",
            "the corpus share counts write sites, not faces: one function can write several "
            "names, and the study does not weight by how often a site ran",
        ],
    }


def tally_problems(face: dict) -> list[str]:
    """The checks that need nothing but the face itself (the corpus re-derivation is separate)."""
    problems: list[str] = []
    for r in face["rows"]:
        if r["classification"] not in CLASS_VOCAB:
            problems.append(f"{r['face']}: class outside the frozen vocabulary")
            continue
        if r["hop_kind"] not in (HOP_CONST, HOP_CALLER, HOP_NONE):
            problems.append(f"{r['face']}: hop kind outside the frozen vocabulary")
        if r["classification"] in (W_DATE, W_NODATE) and not r.get("opener"):
            problems.append(f"{r['face']}: graded a writer but the site does not open for writing")
        if r["classification"] in (W_DATE, W_NODATE):
            basis = r.get("date_basis") or {}
            carries = bool(basis.get("payload_keys_with_a_date"))
            holds = bool(basis.get("date_variables_in_scope") or basis.get("date_calls_in_scope"))
            if r["classification"] == W_DATE and not (carries and holds):
                problems.append(f"{r['face']}: graded with-a-date but carries={carries} "
                                f"holds={holds}")
            if r["classification"] == W_NODATE and carries:
                problems.append(f"{r['face']}: graded without-a-date but its payload carries one")
    tally: dict[str, int] = {}
    for r in face["rows"]:
        tally[r["classification"]] = tally.get(r["classification"], 0) + 1
    if tally != face["summary"]["by_class"]:
        problems.append("by_class does not re-derive from the rows")
    moved = sum(1 for r in face["rows"] if r["classification"] in (W_DATE, W_NODATE))
    if moved != face["summary"]["rows_that_became_writers"]:
        problems.append("rows_that_became_writers does not re-derive")
    c = face["summary"]["corpus"]
    if sum(c[k] for k in ("path_spells_a_literal_only", "path_is_parameter_derived_only",
                          "literal_and_parameter", "neither")) != face["summary"]["write_sites"]:
        problems.append("the corpus split does not re-add to the write sites")
    return problems


def verify(face: dict | None = None) -> list[str]:
    """Re-derive the attribution from the tree and refuse a face that does not match."""
    face = face or _load(os.path.join(OUTDIR, "twohop_latest.json"))
    problems = tally_problems(face)
    e419_face = _load(E419_FACE)
    expected = {r["face"] for r in e419_face["rows"] if r["classification"] == E419_MISSING}
    got = {r["face"] for r in face["rows"]}
    if expected != got:
        problems.append(f"population drifted: missing={sorted(expected - got)} "
                        f"extra={sorted(got - expected)}")
    sources = corpus()
    sites, parsed = scan_corpus(sources)
    wanted = {s.func for found in sites.values() for s in found
              if s.parameter_directories() and not s.spells_a_literal()}
    index = main_call_index(wanted, sources)
    for r in face["rows"]:
        if r["classification"] not in CLASS_VOCAB:
            continue
        base, dir_tok, _ = e419.name_pattern(r["face"])
        if r["name_token"] != base or r["directory_token"] != dir_tok:
            problems.append(f"{r['face']}: the published tokens do not re-derive")
        fresh = attribute(r["face"], base, dir_tok, sites, index)
        if fresh["classification"] != r["classification"]:
            problems.append(f"{r['face']}: class re-derives as {fresh['classification']}, "
                            f"published {r['classification']}")
        if r["classification"] in (W_DATE, W_NODATE) and fresh.get("hop_kind") != r.get("hop_kind"):
            problems.append(f"{r['face']}: hop kind re-derives as {fresh.get('hop_kind')}")
    # corpus_sources is a DECLARED population key, not a decision number: the corpus grows when
    # any lane adds a .py file, and equality-gating it reds an honest face (the r1441 law, which
    # this study already declares in POPULATION_KEYS -- the first draft then gated it anyway).
    if int(face["summary"].get("corpus_sources") or 0) <= 0:
        problems.append("corpus_sources is not a positive count")
    return problems


FIXTURE_FILES = {
    "const_hop.py": (
        "import json, os\n"
        "ROOT = '/x'\n"
        "OUT_DIR = os.path.join(ROOT, 'results', 'constface')\n"
        "def write_card(out):\n"
        "    with open(os.path.join(OUT_DIR, 'CARD.md'), 'w') as fh:\n"
        "        fh.write('x')\n"
    ),
    "alias_hop.py": (
        "import os\n"
        "ROOT = '/x'\n"
        "DOC_DIR = os.path.join(ROOT, 'docs', 'lane')\n"
        "def run(bar):\n"
        "    page = os.path.join(DOC_DIR, 'TSM-%s.md' % bar)\n"
        "    with open(page, 'w') as fh:\n"
        "        fh.write('x')\n"
    ),
    "caller_hop.py": (
        "import json, os\n"
        "OUTDIR = os.path.join('/x', 'results', 'state_tilt')\n"
        "def _write(face, outdir):\n"
        "    name = 'AGG-%s.json' % face\n"
        "    with open(os.path.join(outdir, name), 'w') as fh:\n"
        "        fh.write('{}')\n"
        "def run(outdir=None):\n"
        "    outdir = outdir or OUTDIR\n"
        "    _write({}, outdir)\n"
    ),
    "reader_only.py": (
        "import os\n"
        "def read_card():\n"
        "    with open(os.path.join('/x', 'results', 'constface', 'CARD.md')) as fh:\n"
        "        return fh.read()\n"
    ),
    "no_caller.py": (
        "import os\n"
        "def _write_ghost(face, outdir):\n"
        "    with open(os.path.join(outdir, 'GHOST-%s.json' % face), 'w') as fh:\n"
        "        fh.write('{}')\n"
    ),
}


def selftest() -> int:
    import shutil
    import tempfile
    bad = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal bad
        if cond:
            print(f"[PASS] {name}")
        else:
            bad += 1
            print(f"[FAIL] {name} {detail}")

    tmp = tempfile.mkdtemp(prefix="e429_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
        sites: dict[str, list[Site]] = {}
        for fn, text in FIXTURE_FILES.items():
            rel = "scripts/" + fn
            full = os.path.join(tmp, rel)
            with io.open(full, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            sites[rel] = scan_file(full, text)
        wanted = {s.func for found in sites.values() for s in found
                  if s.parameter_directories() and not s.spells_a_literal()}
        index: dict[str, list[dict]] = {n: [] for n in wanted}
        for fn, text in FIXTURE_FILES.items():
            rel = "scripts/" + fn
            for call, owner in _iter_calls(ast.parse(text)):
                name = e419._call_name(call)
                if name in index:
                    lines = text.splitlines()
                    fenv = function_env(owner, lines) if owner is not None else {}
                    index[name].append({
                        "file": rel, "caller": getattr(owner, "name", "<module>"),
                        "line": call.lineno,
                        "args": [seg(lines, a) for a in call.args],
                        "kwargs": {kw.arg: seg(lines, kw.value)
                                   for kw in call.keywords if kw.arg},
                        "env": dict(module_env(ast.parse(text), lines), **fenv)})

        r_const = attribute("results/constface/CARD.md", "CARD", "constface", sites, index)
        check("a directory held in a module constant is followed",
              r_const["classification"] in (W_DATE, W_NODATE)
              and r_const["hop_kind"] == HOP_CONST, r_const["classification"])

        r_alias = attribute("docs/lane/TSM-%s.md", "TSM-", "lane", sites, index)
        check("a local alias of a constant is followed (two substitutions)",
              r_alias["classification"] in (W_DATE, W_NODATE)
              and r_alias["hop_kind"] == HOP_CONST, r_alias.get("resolved_path"))

        r_caller = attribute("results/state_tilt/AGG-%s.json", "AGG-", "state_tilt", sites, index)
        check("a helper that takes the directory is followed to its caller",
              r_caller["classification"] in (W_DATE, W_NODATE)
              and r_caller["hop_kind"] == HOP_CALLER, r_caller["classification"])
        check("the caller site is published, not just counted",
              bool(r_caller.get("supplied_at"))
              and r_caller["supplied_at"][0]["function"] == "run",
              r_caller.get("supplied_at"))

        r_ghost = attribute("results/state_tilt/GHOST-%s.json", "GHOST-", "state_tilt",
                            sites, index)
        check("a helper with no caller supplying the directory is not a writer",
              r_ghost["classification"] == W_HELPER, r_ghost["classification"])

        r_missing = attribute("results/nowhere/NOPE.md", "NOPE", "nowhere", sites, index)
        check("a name nobody writes stays no-writer", r_missing["classification"] == W_STILL,
              r_missing["classification"])

        # A reader of the face must not become its writer.
        reader_sites = {k: v for k, v in sites.items() if k.endswith("reader_only.py")}
        r_reader = attribute("results/constface/CARD.md", "CARD", "constface", reader_sites, index)
        check("a function that opens the face for reading is not a writer",
              r_reader["classification"] == W_STILL, r_reader["classification"])

        # The corpus split must count a parameter path as needing a hop even when a literal
        # sits in the same expression (join(outdir, "X.json")).
        agg = [s for found in sites.values() for s in found if s.func == "_write_ghost"][0]
        check("a literal in the path does not hide the parameter that supplies its directory",
              agg.spells_a_literal() and bool(agg.parameter_directories()),
              (agg.paths, agg.parameter_directories()))

        # A self-referential default argument must resolve instead of looping.
        text = resolve("outdir", [{"outdir": "outdir or OUTDIR",
                                   "OUTDIR": "'/x/results/state_tilt'"}], hops=3)
        check("a self-referential binding terminates and reaches the constant",
              "state_tilt" in text and len(text) < MAX_TEXT, text[:80])

        face = {
            "rows": [{"face": "a", "classification": W_STILL, "hop_kind": HOP_NONE,
                      "opener": False, "name_token": "a", "directory_token": None}],
            "summary": {"by_class": {W_STILL: 2}, "rows_that_became_writers": 0,
                        "write_sites": 4,
                        "corpus": {"path_spells_a_literal_only": 1,
                                   "path_is_parameter_derived_only": 1,
                                   "literal_and_parameter": 1, "neither": 1},
                        "corpus_sources": 0},
        }
        problems = tally_problems(face)
        check("verify refuses a by_class that does not re-derive",
              any("by_class" in p for p in problems), problems)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    total = 11
    print(f"selftest {'PASS' if not bad else 'FAIL'} {total - bad}/{total}")
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print(f"verify problems={len(problems)}")
        return 0 if not problems else 1
    face = build()
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"TWOHOP-{face['evidence_cutoff']}.json")
    for target in (out, os.path.join(OUTDIR, "twohop_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print(f"population={s['faces_in_population']} became_writers={s['rows_that_became_writers']} "
          f"with_date={s['rows_with_a_date']} without_date={s['rows_without_a_date']}")
    print(f"by_class={s['by_class']}")
    print(f"corpus={s['corpus']} write_sites={s['write_sites']}")
    print(f"reach={s['two_hop_reach']}")
    print(f"verdict={face['verdict']}")
    print(f"face={_rel(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))