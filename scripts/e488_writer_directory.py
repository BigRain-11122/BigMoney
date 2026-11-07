"""E488 -- for the basename-only writers, does the module's own directory constant name the reader dir?

E487 traced 67 of 84 unwritten ``*_latest.json`` spellings back to a writing source, but only 1 of
those writer paths reached the directory its reader resolves to: 51 reached a *bare basename* and
were published as "the directory is untraced".  A basename-only class is an unfinished trace, not a
finding: the write call often looks like ``write(os.path.join(OUTDIR, NAME), payload)`` where the
basename comes from the traced literal and the directory from a module constant one indirection
away (``OUTDIR = e451.OUTDIR``, ``OUTDIR = os.path.join(ROOT, "results", "state_tilt")``).

This face finishes that trace for the 51 rows and splits them by what the module's own directory
expression says.  Nothing about the writer's existence changes -- the question is *where* it writes.

Fold rules (each published on the row as evidence):
  literal           a string that carries a separator is a path
  name              a module-level or same-function assignment is folded, up to MAX_HOPS
  join              ``os.path.join(a, b, ...)`` folds as the cartesian concatenation
  add               ``a + b`` folds when both sides fold to strings
  file              ``os.path.dirname(...(os.path.abspath(__file__)))`` folds to the module's own
                    parent directory, walked up once per ``dirname`` wrapper (the repo root is
                    published as the empty string, so a join with it yields a repo-relative path)
  alias             ``alias.NAME`` where ``alias`` is a module in this repository folds into that
                    module's own binding (one hop per level, bounded), never into a third-party one

Anything else (argv, os.environ, a function parameter, a dict key, ``%``-formatted stems) is
*unresolved*, and a row whose only directory expression is unresolved is published as such --
never folded into the "names another directory" class, which is a positive statement.

Run:      python scripts/e488_writer_directory.py run
Verify:   python scripts/e488_writer_directory.py verify
Check:    python scripts/e488_writer_directory.py check
Selftest: python scripts/e488_writer_directory.py selftest
"""

import argparse
import ast
import io
import json
import os
import re
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402
import e468_pointer_reach as e468  # noqa: E402
import e487_composed_writer as e487  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "writerdir_latest.json"
DATED_PREFIX = "WRITERDIR"
CARD = "E488-FOR-THE-BASENAME-ONLY-WRITERS-DOES-THE-MODULE-OWN-DIRECTORY-CONSTANT-NAME-THE-READER-DIRECTORY"

PARENT_FACE = "composedwriter_latest.json"          # E487
TRACED_CLASSES = e487.TRACED
POPULATION_DIRECTORY_CLASS = e487.D_BASENAME_ONLY

EXCLUDED_PREFIX = e487.EXCLUDED_PREFIX + ("e488_", "run_e488")
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_HOPS = 12
MAX_EXPRESSIONS_PER_ROW = 12
MAX_PATHS_PER_EXPRESSION = 8
MAX_SOURCES_PER_ROW = 8

# ---- per-row classes --------------------------------------------------------------------------
K_SAME = "the_module_directory_expression_names_the_reader_directory"
K_ANCESTOR = "the_module_directory_expression_names_an_ancestor_of_the_reader_directory"
K_OTHER = "the_module_directory_expression_names_a_directory_that_is_not_the_reader_directory"
K_UNRESOLVED = "the_module_states_a_directory_expression_that_cannot_be_folded_statically"
K_NONE = "the_module_states_no_directory_expression_at_all"
CLASSES = (K_SAME, K_ANCESTOR, K_OTHER, K_UNRESOLVED, K_NONE)

DIR_NAME_RE = re.compile(
    r"(dir|dirs|path|paths|root|home|base|out|outdir|face|faces|result|results|tilt|store|home_"
    r"dir)$", re.I)


def _norm(text):
    return str(text or "").replace("\\", "/").strip()


def _clean(path):
    """Normalise a folded path: repo root is '', './x' and 'x/' both become 'x'."""
    p = _norm(path)
    while p.startswith("./"):
        p = p[2:]
    while p.endswith("/") and len(p) > 1:
        p = p[:-1]
    if p == ".":
        p = ""
    return p


def _looks_like_path(value):
    v = _norm(value)
    return "/" in v or v in ("", ".")


# ------------------------------------------------------------------ population


def population(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    face = json.load(io.open(path, "r", encoding="utf-8"))
    summary = face.get("summary") or {}
    rows = [r for r in face.get("rows") or []
            if r.get("class") in TRACED_CLASSES
            and r.get("directory_class") == POPULATION_DIRECTORY_CLASS]
    published = (summary.get("directory_class_counts") or {}).get(POPULATION_DIRECTORY_CLASS)
    parent = {
        "face": PARENT_FACE,
        "face_verdict": face.get("verdict"),
        "face_evidence_cutoff": face.get("evidence_cutoff"),
        "parent_directory_class_counts": summary.get("directory_class_counts"),
        "parent_basename_only_spellings": published,
        "population_rows_agree_with_the_parent_tally": published == len(rows),
        "population_definition": "rows of E487 class in {direct,helper,loop} with directory_class "
                                 "== the basename-only class",
        "excluded_source_prefixes": list(EXCLUDED_PREFIX),
    }
    return rows, parent


# ------------------------------------------------------------------ expression folding


def _module_alias_map(tree):
    """alias -> module name for ``import x as alias`` / ``import x`` / ``from x import y``."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                local = a.asname or a.name.split(".")[-1]
                out[local] = a.name
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                for a in node.names:
                    out[a.asname or a.name] = node.module
    return out


def _file_depth(node):
    """How many ``dirname`` wrappers sit around ``__file__`` (None if the shape is not that)."""
    depth = 0
    cur = node
    while isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute) \
            and cur.func.attr == "dirname" and len(cur.args) == 1:
        depth += 1
        cur = cur.args[0]
    while isinstance(cur, ast.Call) and len(cur.args) == 1 and (
            (isinstance(cur.func, ast.Name) and cur.func.id == "abspath")
            or (isinstance(cur.func, ast.Attribute) and cur.func.attr == "abspath")):
        cur = cur.args[0]
    if isinstance(cur, ast.Name) and cur.id == "__file__":
        return depth
    return None


def _walk_up(rel_dir, depth):
    base = rel_dir
    for _ in range(depth):
        base = os.path.dirname(base).replace("\\", "/")
        if base in (".", "/"):
            base = ""
    return base


class Folder(object):
    """Static folder over one module: module-level and function-level string constants."""

    def __init__(self, rel, tree, root, depth=0, cache=None):
        self.rel = rel
        self.tree = tree
        self.root = root
        self.depth = depth
        self.cache = cache if cache is not None else {}
        self.alias = _module_alias_map(tree)
        self.module_bindings = {}
        self.calls = []
        for node in tree.body:
            self._bind(node)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self.calls.append(node)

    # -- bindings
    def _bind(self, node, into=None):
        into = self.module_bindings if into is None else into
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    into.setdefault(target.id, node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
            into.setdefault(node.target.id, node.value)

    def function_bindings(self, line):
        """Bindings of the innermost function containing ``line`` (plus the module's own)."""
        best = None
        for node in ast.walk(self.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            start = getattr(node, "lineno", 0)
            end = getattr(node, "end_lineno", start) or start
            if start <= line <= end:
                if best is None or start > getattr(best, "lineno", 0):
                    best = node
        out = dict(self.module_bindings)
        if best is not None:
            local = {}
            for node in ast.walk(best):
                self._bind(node, local)
            for k, v in local.items():
                out[k] = v
        return out

    # -- folding
    def fold(self, node, names, depth=0):
        """Return (paths, unresolved) for an expression node."""
        if depth > MAX_HOPS:
            return [], True
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return [node.value], False
        if isinstance(node, ast.JoinedStr):
            if all(isinstance(v, ast.Constant) for v in node.values):
                return [str(v.value) for v in node.values], False
            return [], True
        if isinstance(node, ast.Name):
            target = names.get(node.id)
            if target is None:
                if node.id == "__file__":
                    return [self._self_dir()], False
                return [], True
            return self.fold(target, names, depth + 1)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Div)):
            left, lu = self.fold(node.left, names, depth + 1)
            right, ru = self.fold(node.right, names, depth + 1)
            if not left or not right:
                return [], True
            sep = "/" if isinstance(node.op, ast.Div) else ""
            return ["%s%s%s" % (a, sep, b) for a in left[:MAX_PATHS_PER_EXPRESSION]
                    for b in right[:MAX_PATHS_PER_EXPRESSION]], (lu or ru)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            alias = node.value.id
            mod = self.alias.get(alias)
            if mod:
                return self._fold_foreign(mod, node.attr, depth)
            return [], True
        if isinstance(node, ast.Call):
            depth_hint = _file_depth(node)
            if depth_hint is not None:
                return [self._self_dir(extra_up=depth_hint)], False
            name = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if name == "join":
                parts = []
                unresolved = False
                for arg in node.args:
                    paths, una = self.fold(arg, names, depth + 1)
                    if not paths:
                        return [], True
                    parts.append(paths[:MAX_PATHS_PER_EXPRESSION])
                    unresolved = unresolved or una
                acc = [""]
                for options in parts:
                    acc = [self._join(a, b) for a in acc for b in options][
                        :MAX_PATHS_PER_EXPRESSION]
                return acc, unresolved
            if name in ("dirname", "abspath", "normpath", "realpath") and len(node.args) == 1:
                paths, una = self.fold(node.args[0], names, depth + 1)
                if not paths:
                    return [], True
                if name == "dirname":
                    return [os.path.dirname(p).replace("\\", "/") for p in paths], una
                return paths, una
            return [], True
        return [], True

    def _self_dir(self, extra_up=0):
        base = os.path.dirname(self.rel).replace("\\", "/")
        return _walk_up(base, extra_up)

    @staticmethod
    def _join(a, b):
        a, b = _clean(a), _clean(b)
        if not a:
            return b
        if not b:
            return a
        if a.endswith("/"):
            return a + b
        return a + "/" + b

    def _fold_foreign(self, module_name, attr, depth):
        rel = self._find_module(module_name)
        if rel is None or depth > MAX_HOPS:
            return [], True
        if rel in self.cache:
            foreign = self.cache[rel]
        else:
            try:
                text = e451.read_text(os.path.join(self.root, rel))
                foreign = Folder(rel, ast.parse(text), self.root, depth + 1, self.cache)
            except (OSError, SyntaxError):
                self.cache[rel] = None
                return [], True
            self.cache[rel] = foreign
        if foreign is None:
            return [], True
        if attr in foreign.module_bindings:
            return foreign.fold(foreign.module_bindings[attr], foreign.module_bindings,
                                depth + 1)
        return [], True

    def _find_module(self, module_name):
        tail = module_name.replace(".", "/")
        for base in ("scripts/", "", "Tools/", "firm/"):
            rel = "%s%s.py" % (base, tail)
            if os.path.isfile(os.path.join(self.root, rel)):
                return rel
        return None


def module_directory_expressions(root, rel, line=None):
    """Directory-shaped constants of one module, folded.  Each entry is published evidence."""
    path = os.path.join(root, rel)
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return [], "the_source_is_larger_than_the_read_cap"
        tree = ast.parse(e451.read_text(path))
    except (OSError, SyntaxError):
        return [], "the_source_cannot_be_parsed"
    folder = Folder(rel, tree, root)
    names = folder.function_bindings(line) if line else folder.module_bindings
    expressions = []
    for name in sorted(names):
        if not DIR_NAME_RE.search(name or ""):
            continue
        node = names[name]
        paths, unresolved = folder.fold(node, names)
        cleaned = []
        for p in paths:
            c = _clean(p)
            if c in cleaned:
                continue
            # a single-segment directory name ("results") carries no separator, so it is kept
            # only when it names a directory that exists under the repository root: a constant
            # that folds to a bare word nobody can place stays out of the resolved set
            if _looks_like_path(c) or os.path.isdir(os.path.join(root, c)):
                cleaned.append(c)
        try:
            text = ast.get_source_segment(
                io.open(path, "r", encoding="utf-8", errors="replace").read(), node) or name
        except (OSError, SyntaxError):
            text = name
        expressions.append({
            "name": name,
            "expression": str(text).strip()[:200],
            "resolved_paths": cleaned[:MAX_PATHS_PER_EXPRESSION],
            "unresolved": bool(unresolved) or not cleaned,
        })
    if not expressions:
        return [], "the_module_states_no_directory_shaped_constant"
    return expressions[:MAX_EXPRESSIONS_PER_ROW], None


# ------------------------------------------------------------------ classify


def directory_class_of(reader_directories, expressions):
    """Re-derive the row class from published evidence (this is what ``check`` runs)."""
    readers = [_clean(d) for d in reader_directories if _clean(d)]
    resolved = []
    unresolved_seen = False
    for expr in expressions or []:
        if expr.get("unresolved"):
            unresolved_seen = True
        for p in expr.get("resolved_paths") or []:
            c = _clean(p)
            if c:
                resolved.append(c)
    if not resolved:
        return K_UNRESOLVED if unresolved_seen else K_NONE
    for path in resolved:
        for reader in readers:
            if path == reader:
                return K_SAME
    for path in resolved:
        for reader in readers:
            if path and reader.startswith(path + "/"):
                return K_ANCESTOR
    return K_OTHER


def classify(root=None, rows_input=None):
    rows_in, parent = rows_input if rows_input else population(root)
    rows = []
    for row in sorted(rows_in, key=lambda r: str(r.get("spelling"))):
        readers = [_clean(d) for d in (row.get("resolved_directories") or [])]
        sources = []
        expressions = []
        notes = []
        for src in (row.get("tracing_sources") or [])[:MAX_SOURCES_PER_ROW]:
            rel = _norm(src.get("source"))
            if not rel:
                continue
            exprs, note = module_directory_expressions(root, rel, src.get("line"))
            sources.append({"source": rel, "route": src.get("route"), "line": src.get("line"),
                            "directory_expressions_found": len(exprs),
                            "directory_expression_note": note})
            for e in exprs:
                if e not in expressions:
                    expressions.append(e)
            if note and note not in notes:
                notes.append(note)
        klass = directory_class_of(readers, expressions)
        rows.append({
            "spelling": row.get("spelling"),
            "stem": row.get("stem"),
            "parent_class": row.get("class"),
            "parent_route": row.get("route"),
            "parent_directory_class": row.get("directory_class"),
            "reader_directories": readers[:MAX_PATHS_PER_EXPRESSION],
            "tracing_sources": sources,
            "module_directory_expressions": expressions,
            "directory_class": klass,
            "resolved_directory_paths": sorted({p for e in expressions
                                                for p in (e.get("resolved_paths") or [])})[
                :MAX_PATHS_PER_EXPRESSION],
            "notes": notes,
        })
    return rows, parent


# ------------------------------------------------------------------ summary / verdict


def _recompute(face):
    rows = face.get("rows") or []
    counts = {k: 0 for k in CLASSES}
    for row in rows:
        if row.get("directory_class") in counts:
            counts[row["directory_class"]] += 1
    return {
        "population_spellings": len(rows),
        "population_tracing_sources": len({s.get("source") for r in rows
                                           for s in (r.get("tracing_sources") or [])}),
        "directory_class_counts": counts,
        "spellings_whose_writer_module_names_the_reader_directory": counts[K_SAME],
        "spellings_whose_writer_module_names_an_ancestor": counts[K_ANCESTOR],
        "spellings_whose_writer_module_names_another_directory": counts[K_OTHER],
        "spellings_whose_writer_module_directory_is_unfoldable": counts[K_UNRESOLVED],
        "spellings_whose_writer_module_states_no_directory": counts[K_NONE],
        "spellings_now_confirmed_to_write_into_the_reader_directory": counts[K_SAME],
        "spellings_whose_basename_only_class_survives_tracing": counts[K_NONE],
    }


V_EMPTY = "the_parent_published_no_basename_only_spelling"
V_NONE = "no_basename_only_writer_module_names_the_reader_directory"
V_ALL = "every_basename_only_writer_module_names_the_reader_directory"
V_MOST = "most_basename_only_writer_modules_name_the_reader_directory"
V_MINORITY = "a_minority_of_basename_only_writer_modules_name_the_reader_directory"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST, V_MINORITY)


def _verdict(summary):
    total = int(summary.get("population_spellings") or 0)
    if not total:
        return V_EMPTY
    same = int(summary.get("spellings_whose_writer_module_names_the_reader_directory") or 0)
    if same == 0:
        return V_NONE
    if same == total:
        return V_ALL
    return V_MOST if same * 2 >= total else V_MINORITY


# ------------------------------------------------------------------ build / write


def build(root=None, write=True):
    root = root or ROOT
    rows, parent = classify(root)
    summary = _recompute({"rows": rows})
    summary["parent_basename_only_spellings"] = parent["parent_basename_only_spellings"]
    summary["population_reproduced"] = parent["population_rows_agree_with_the_parent_tally"]
    face = {
        "card": CARD,
        "study": "E488_for_the_basename_only_writers_does_the_module_own_directory_constant_"
                 "name_the_reader_directory",
        "title": "for the basename-only writers, does the module's own directory constant name the "
                 "reader directory?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": parent,
        "fold_rule": {
            "literal": "a string constant that carries '/' is a path",
            "name": "module-level and same-function assignments are folded up to %d hops" % MAX_HOPS,
            "join": "os.path.join(a, b, ...) folds as the cartesian concatenation; the repo root "
                    "folds to the empty string so the first part is written repo-relative",
            "add": "a + b folds when both sides fold to strings",
            "file": "os.path.dirname(...(os.path.abspath(__file__))) folds to the module's own "
                    "parent, walked up once per dirname wrapper",
            "alias": "alias.NAME folds into that module's own binding when the module exists in "
                     "this repository and is imported by this file; a third-party module is "
                     "unresolved",
        },
        "class_definition": {
            K_SAME: "a folded directory path equals the directory the reader resolves to",
            K_ANCESTOR: "a folded directory path is a strict ancestor of the reader's directory, "
                        "so the subdirectory is named somewhere this fold does not follow",
            K_OTHER: "the module folds directory paths and none is the reader's directory or an "
                     "ancestor of it: the writer is placed somewhere else",
            K_UNRESOLVED: "the module has directory-shaped constants but none folds to a path "
                          "(argv, os.environ, parameters, dict keys)",
            K_NONE: "the module has no directory-shaped constant at all",
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "the fold reads one module per tracing source and follows one hop into an imported "
            "repository module; a directory built from a function parameter, argv, os.environ or a "
            "dict key is published unresolved, never as a directory statement",
            "K_OTHER is a positive statement only when a folded path exists; a module that folds "
            "nothing is K_UNRESOLVED or K_NONE",
            "K_SAME says the module names the reader's directory, not that the write happens there "
            "at run time: the write path itself was traced by E487 to a bare basename, so a "
            "runtime-composed suffix can still differ",
            "the population is E487's basename-only arm, kept byte-for-byte as published; this "
            "face adds a directory question and does not re-open the parent's class question",
            "the repo root folds to the empty string because these modules compute ROOT from "
            "__file__; a module that hardcodes a relative path is compared repo-relative too, so "
            "both spellings land on the same string",
        ],
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(outdir, FACE_NAME)
    body = json.dumps(face, indent=1, ensure_ascii=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return dated, latest


# ------------------------------------------------------------------ check / verify


def row_problems(face):
    problems = []
    summary = face.get("summary") or {}
    derived = _recompute(face)
    for key, value in derived.items():
        if summary.get(key) != value:
            problems.append("%s: published %r, re-derives %r" % (key, summary.get(key), value))
    seen = set()
    for row in face.get("rows") or []:
        spelling = row.get("spelling")
        if spelling in seen:
            problems.append("%s: duplicated row" % (spelling,))
        seen.add(spelling)
        klass = row.get("directory_class")
        if klass not in CLASSES:
            problems.append("%s: unknown class %r" % (spelling, klass))
        expected = directory_class_of(row.get("reader_directories") or [],
                                      row.get("module_directory_expressions") or [])
        if klass != expected:
            problems.append("%s: class %r does not re-derive as %r" % (spelling, klass, expected))
        if klass == K_NONE and row.get("module_directory_expressions"):
            problems.append("%s: the no-expression class beside published expressions"
                            % (spelling,))
        if klass in (K_SAME, K_ANCESTOR, K_OTHER) and not row.get(
                "resolved_directory_paths"):
            problems.append("%s: a placed writer publishes no resolved path" % (spelling,))
        if row.get("parent_directory_class") != POPULATION_DIRECTORY_CLASS:
            problems.append("%s: row is not from the parent's basename-only arm" % (spelling,))
    if _verdict({k: summary.get(k) for k in derived}) != face.get("verdict"):
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"),
                           _verdict({k: summary.get(k) for k in derived})))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e488 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    s = face.get("summary") or {}
    print("population=%d same=%d ancestor=%d other=%d unresolved=%d none=%d"
          % (s.get("population_spellings") or 0,
             s.get("spellings_whose_writer_module_names_the_reader_directory") or 0,
             s.get("spellings_whose_writer_module_names_an_ancestor") or 0,
             s.get("spellings_whose_writer_module_names_another_directory") or 0,
             s.get("spellings_whose_writer_module_directory_is_unfoldable") or 0,
             s.get("spellings_whose_writer_module_states_no_directory") or 0))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build(root, write=False)
    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved")
    a = {r["spelling"]: r for r in published.get("rows") or []}
    b = {r["spelling"]: r for r in fresh.get("rows") or []}
    if set(a) != set(b):
        problems.append("population moved: +%d -%d" % (len(set(b) - set(a)),
                                                       len(set(a) - set(b))))
    for spelling in sorted(set(a) & set(b)):
        if a[spelling].get("directory_class") != b[spelling].get("directory_class"):
            problems.append("%s: class moved %r -> %r" % (spelling,
                                                          a[spelling].get("directory_class"),
                                                          b[spelling].get("directory_class")))
    problems.extend(row_problems(fresh))
    print("e488 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir)
    os.makedirs(os.path.join(root, "scripts"))

    def row(spelling, source, line=10, directory="results/state_tilt"):
        return {"spelling": spelling, "stem": spelling.replace("_latest.json", ""),
                "class": e487.C_DIRECT, "route": "direct",
                "directory_class": POPULATION_DIRECTORY_CLASS,
                "resolved_directories": [directory],
                "resolved_paths": ["%s/%s" % (directory, spelling)],
                "tracing_sources": [{"source": source, "route": "direct", "line": line}],
                "reader_sources": ["smoke_test.py"], "reader_source_count": 1,
                "tracing_source_count": 1}

    rows = [
        row("samestem_latest.json", "scripts/w_same.py"),
        row("aliasstem_latest.json", "scripts/w_alias.py"),
        row("ancestorstem_latest.json", "scripts/w_ancestor.py"),
        row("otherstem_latest.json", "scripts/w_other.py"),
        row("envstem_latest.json", "scripts/w_unresolved.py"),
        row("plainstem_latest.json", "scripts/w_none.py"),
    ]
    parent = {
        "verdict": e487.V_MOST_TRACED,
        "evidence_cutoff": "2026-11-07",
        "summary": {"distinct_spellings": 8,
                    "class_counts": {e487.C_DIRECT: len(rows)},
                    "directory_class_counts": {POPULATION_DIRECTORY_CLASS: len(rows),
                                               e487.D_SAME: 1}},
        "rows": rows + [{"spelling": "insame_latest.json", "class": e487.C_DIRECT,
                         "route": "direct", "directory_class": e487.D_SAME,
                         "resolved_directories": ["results/state_tilt"],
                         "resolved_paths": ["results/state_tilt/insame_latest.json"],
                         "tracing_sources": [], "reader_sources": []}],
        "verdict_vocab": list(e487.VERDICT_VOCAB),
    }
    io.open(os.path.join(outdir, PARENT_FACE), "w", encoding="utf-8",
            newline="\n").write(json.dumps(parent))
    io.open(os.path.join(root, "scripts", "shared_dirs.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n")
    io.open(os.path.join(root, "scripts", "w_same.py"), "w", encoding="utf-8", newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n"
        "NAME = 'samestem_latest.json'\n"
        "open(os.path.join(OUTDIR, NAME), 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_alias.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import shared_dirs\n"
        "OUTDIR = shared_dirs.OUTDIR\n"
        "NAME = 'aliasstem_latest.json'\n"
        "open(OUTDIR + '/' + NAME, 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_ancestor.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "RESULT_ROOT = os.path.join(ROOT, 'results')\n"
        "open(os.path.join(RESULT_ROOT, 'state_tilt', 'ancestorstem_latest.json'), 'w')\n")
    io.open(os.path.join(root, "scripts", "w_other.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'quarantine')\n"
        "open(os.path.join(OUTDIR, 'otherstem_latest.json'), 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_unresolved.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os, sys\n"
        "OUTDIR = sys.argv[1]\n"
        "open(os.path.join(OUTDIR, 'envstem_latest.json'), 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_none.py"), "w", encoding="utf-8",
            newline="\n").write(
        "open('plainstem_latest.json', 'w').write('{}')\n")
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e488_")
    root = _fixture(tmp)
    rows_in, parent = population(root)
    leg("the parent's basename-only arm is the population", len(rows_in) == 6)
    leg("the parent's tally is reproduced", parent["population_rows_agree_with_the_parent_tally"])
    leg("the parent count is carried", parent["parent_basename_only_spellings"] == 6)
    leg("a repo-root fold is the empty string",
        _clean(".") == "" and _clean("./") == "")
    leg("a module folds its __file__ chain to the repo root",
        module_directory_expressions(root, "scripts/w_same.py", 4)[0][0]["resolved_paths"]
        == ["results/state_tilt"])
    rows, _ = classify(root)
    by = {r["spelling"]: r for r in rows}
    leg("a same-directory module is K_SAME",
        by["samestem_latest.json"]["directory_class"] == K_SAME)
    leg("an aliased module constant is folded into the repository module",
        by["aliasstem_latest.json"]["directory_class"] == K_SAME)
    leg("a results-root module is K_ANCESTOR",
        by["ancestorstem_latest.json"]["directory_class"] == K_ANCESTOR)
    leg("a quarantine module is K_OTHER",
        by["otherstem_latest.json"]["directory_class"] == K_OTHER)
    leg("a sys.argv directory is K_UNRESOLVED",
        by["envstem_latest.json"]["directory_class"] == K_UNRESOLVED)
    leg("a module with no directory constant is K_NONE",
        by["plainstem_latest.json"]["directory_class"] == K_NONE)
    leg("the class re-derives from the published row evidence",
        directory_class_of(by["otherstem_latest.json"]["reader_directories"],
                           by["otherstem_latest.json"]["module_directory_expressions"]) == K_OTHER)
    leg("an ancestor is not confused with the reader directory",
        directory_class_of(["results/state_tilt"], [
            {"name": "X", "resolved_paths": ["results"], "unresolved": False}]) == K_ANCESTOR)
    leg("a deeper directory is not an ancestor",
        directory_class_of(["results"], [
            {"name": "X", "resolved_paths": ["results/state_tilt"], "unresolved": False}])
        == K_OTHER)
    face = {"rows": rows, "evidence_cutoff": "2026-11-07"}
    summary = _recompute(face)
    face["summary"] = summary
    face["verdict"] = _verdict(summary)
    leg("the tallies re-derive", summary["population_spellings"] == len(rows))
    leg("every row lands in exactly one class",
        sum(summary["directory_class_counts"].values()) == len(rows))
    leg("the same-directory count is the headline",
        summary["spellings_whose_writer_module_names_the_reader_directory"] == 2)
    leg("the fixture has no row problems", row_problems(face) == [])
    broken = json.loads(json.dumps(face))
    next(r for r in broken["rows"]
         if r["directory_class"] == K_OTHER)["directory_class"] = K_SAME
    leg("a class that does not re-derive is refused", row_problems(broken))
    broken2 = json.loads(json.dumps(face))
    broken2["verdict"] = V_ALL
    leg("a verdict that does not re-derive is refused", row_problems(broken2))
    broken3 = json.loads(json.dumps(face))
    next(r for r in broken3["rows"]
         if r["directory_class"] == K_OTHER)["resolved_directory_paths"] = []
    leg("a placed class with no resolved path is refused", row_problems(broken3))
    broken4 = json.loads(json.dumps(face))
    broken4["rows"][0]["parent_directory_class"] = e487.D_SAME
    leg("a row outside the basename-only arm is refused", row_problems(broken4))
    leg("write leaves both faces on disk",
        all(os.path.exists(p) for p in _write(face, root)))
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def run(root=None):
    root = root or ROOT
    face = build(root, write=True)
    s = face["summary"]
    print("e488 run verdict=%s" % face["verdict"])
    print("population=%d same=%d ancestor=%d other=%d unresolved=%d none=%d reproduced=%s"
          % (s["population_spellings"],
             s["spellings_whose_writer_module_names_the_reader_directory"],
             s["spellings_whose_writer_module_names_an_ancestor"],
             s["spellings_whose_writer_module_names_another_directory"],
             s.get("spellings_whose_writer_module_directory_is_unfoldable"),
             s["spellings_whose_writer_module_states_no_directory"],
             s.get("population_reproduced")))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E488 where the basename-only writers actually write")
    ap.add_argument("mode", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.mode == "check":
        return check()
    if args.mode == "verify":
        return verify()
    if args.mode == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())