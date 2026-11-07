"""E489 -- does the traced write call join the very constant that placed its row?

E488 (r1513) placed 50 of the 51 basename-only writers in the reader's directory by
folding the module's *directory-shaped constant*.  That is a claim about the module,
not about the write call: E487 had traced the write path only as far as a bare
basename.  This face closes that gap: for each E488 same-directory row it takes the
recorded write site, folds the *write call's own path argument* (following the
loop variable it is passed through) and asks whether it literally composes
``<reader directory>/<spelling>``.

Classes (each row lands in exactly one, re-derived from published evidence):
  W_WIRED      the write call folds to the exact path the reader opens
  W_DIR_ONLY   the write call folds into the reader's directory under another basename
  W_ELSEWHERE  the write call folds to a path in another directory
  W_UNFOLDABLE a write call exists but its path argument does not fold
  W_NO_CALL    no write call is published at the recorded site
"""

import argparse
import ast
import io
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402
import e487_composed_writer as e487  # noqa: E402
import e488_writer_directory as e488  # noqa: E402
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "writewire_latest.json"
DATED_PREFIX = "WRITEWIRE"
CARD = ("E489-DOES-THE-TRACED-WRITE-CALL-JOIN-THE-VERY-CONSTANT-THAT-PLACED-ITS-ROW-"
        "IN-THE-READER-DIRECTORY")

PARENT_FACE = "writerdir_latest.json"                      # E488
POPULATION_DIRECTORY_CLASS = e488.K_SAME
EXCLUDED_PREFIX = e488.EXCLUDED_PREFIX + ("e489_", "run_e489")
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_HOPS = 24
MAX_PATHS = 8
MAX_SOURCES_PER_ROW = 8
SEARCH_LINES = 2

W_WIRED = "the_write_call_composes_the_exact_path_the_reader_opens"
W_DIR_ONLY = "the_write_call_composes_the_reader_directory_with_another_basename"
W_ELSEWHERE = "the_write_call_composes_a_path_in_another_directory"
W_UNFOLDABLE = "a_write_call_is_present_but_its_path_argument_does_not_fold"
W_NO_CALL = "no_write_call_is_published_at_the_recorded_site"
CLASSES = (W_WIRED, W_DIR_ONLY, W_ELSEWHERE, W_UNFOLDABLE, W_NO_CALL)

WRITE_FUNCS = ("open", "write_json", "write_json_face", "write_text", "dump_json")
WRITE_ATTRS = ("open", "write_text", "write_bytes", "dump")


def _norm(text):
    return e488._norm(text)


def _clean(path):
    return e488._clean(path)


# ------------------------------------------------------------------ population


def population(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    face = json.load(io.open(path, "r", encoding="utf-8"))
    summary = face.get("summary") or {}
    rows = [r for r in face.get("rows") or []
            if r.get("directory_class") == POPULATION_DIRECTORY_CLASS]
    published = (summary.get("directory_class_counts") or {}).get(
        POPULATION_DIRECTORY_CLASS)
    parent = {
        "face": PARENT_FACE,
        "face_verdict": face.get("verdict"),
        "face_evidence_cutoff": face.get("evidence_cutoff"),
        "parent_directory_class_counts": summary.get("directory_class_counts"),
        "parent_same_directory_spellings": published,
        "population_rows_agree_with_the_parent_tally": published == len(rows),
        "population_definition": "rows of E488 whose directory_class is the same-directory "
                                 "class (the writer module names the reader directory)",
        "excluded_source_prefixes": list(EXCLUDED_PREFIX),
    }
    return rows, parent


# ------------------------------------------------------------------ write-site folding


class FolderEx(e488.Folder):
    """E488's folder plus loop-variable bindings and tuple/list alternatives."""

    def for_bindings(self, line):
        """``for name in (a, b):`` -- bind every loop target to its iterable expression."""
        out = {}
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.For):
                continue
            start = getattr(node, "lineno", 0)
            end = getattr(node, "end_lineno", start) or start
            if not (start <= line <= end):
                continue
            targets = []
            if isinstance(node.target, ast.Name):
                targets = [node.target.id]
            elif isinstance(node.target, (ast.Tuple, ast.List)):
                targets = [t.id for t in node.target.elts if isinstance(t, ast.Name)]
            for name in targets:
                out.setdefault(name, node.iter)
        return out

    def fold(self, node, names, depth=0):
        if depth > MAX_HOPS:
            return [], True
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return [node.value], False
        if isinstance(node, ast.JoinedStr):
            if all(isinstance(v, ast.Constant) for v in node.values):
                return ["".join(str(v.value) for v in node.values)], False
            return [], True
        if isinstance(node, (ast.Tuple, ast.List)):
            paths = []
            unresolved = False
            for elt in node.elts:
                got, una = self.fold(elt, names, depth + 1)
                paths.extend(got[:MAX_PATHS])
                unresolved = unresolved or una or not got
            return paths[:MAX_PATHS], unresolved
        if isinstance(node, ast.Name):
            target = names.get(node.id)
            if target is None:
                if node.id == "__file__":
                    return [self._self_dir()], False
                return [], True
            if target is node:
                return [], True
            return self.fold(target, names, depth + 1)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Div)):
            left, lu = self.fold(node.left, names, depth + 1)
            right, ru = self.fold(node.right, names, depth + 1)
            if not left or not right:
                return [], True
            sep = "/" if isinstance(node.op, ast.Div) else ""
            return ["%s%s%s" % (a, sep, b) for a in left[:MAX_PATHS]
                    for b in right[:MAX_PATHS]], (lu or ru)
        if isinstance(node, ast.BoolOp):
            # ``x or CONST`` / ``x and CONST``: the expression can take any operand's value
            paths = []
            unresolved = False
            for value in node.values:
                got, una = self.fold(value, names, depth + 1)
                paths.extend(got[:MAX_PATHS])
                unresolved = unresolved or una
            return paths[:MAX_PATHS], unresolved
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            # "NAME-%s.json" % value folds when every substituted value folds to a string
            left, lu = self.fold(node.left, names, depth + 1)
            right, ru = self.fold(node.right, names, depth + 1)
            out = []
            for fmt in left:
                if "%" not in fmt:
                    out.append(fmt)
                    continue
                try:
                    if fmt.count("%") == 1:
                        for value in right:
                            out.append(fmt % value)
                    elif len(right) >= fmt.count("%"):
                        out.append(fmt % tuple(right[:fmt.count("%")]))
                except (TypeError, ValueError):
                    pass
            cleaned = [p for p in out if "%" not in p]
            return cleaned[:MAX_PATHS], (lu or ru or not cleaned)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            alias = node.value.id
            mod = self.alias.get(alias)
            if mod:
                return self._fold_foreign(mod, node.attr, depth)
            return [], True
        if isinstance(node, ast.Call):
            depth_hint = e488._file_depth(node)
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
                    parts.append(paths[:MAX_PATHS])
                    unresolved = unresolved or una
                acc = [""]
                for options in parts:
                    acc = [self._join(a, b) for a in acc for b in options][:MAX_PATHS]
                return acc, unresolved
            if name in ("dirname", "abspath", "normpath", "realpath") and len(node.args) == 1:
                paths, una = self.fold(node.args[0], names, depth + 1)
                if not paths:
                    return [], True
                if name == "dirname":
                    return [os.path.dirname(p).replace("\\", "/") for p in paths], una
                return paths, una
            if isinstance(node.func, ast.Attribute) and not node.args \
                    and node.func.attr in ("lower", "upper", "strip", "rstrip", "lstrip"):
                paths, una = self.fold(node.func.value, names, depth + 1)
                method = getattr(str, node.func.attr)
                return [method(p) for p in paths], una
            if isinstance(node.func, ast.Attribute) and node.func.attr == "replace" \
                    and len(node.args) == 2 and not node.keywords:
                paths, una = self.fold(node.func.value, names, depth + 1)
                old, ou = self.fold(node.args[0], names, depth + 1)
                new, nu = self.fold(node.args[1], names, depth + 1)
                if not paths or not old or not new:
                    return [], True
                return [p.replace(o, n) for p in paths for o in old for n in new], (
                    una or ou or nu)
            return [], True
        return [], True

    def _fold_foreign(self, module_name, attr, depth):
        """Like E488's, but foreign modules stay FolderEx so this face's hop budget applies
        one level deep as well."""
        rel = self._find_module(module_name)
        if rel is None or depth > MAX_HOPS:
            return [], True
        if rel in self.cache:
            foreign = self.cache[rel]
        else:
            try:
                text = e451.read_text(os.path.join(self.root, rel))
                foreign = FolderEx(rel, ast.parse(text), self.root, depth + 1, self.cache)
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


def _is_write_call(node):
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in WRITE_FUNCS
    if isinstance(func, ast.Attribute):
        return func.attr in WRITE_ATTRS
    return False


def write_call_at(tree, line):
    """The innermost write call whose own line is ``line`` (then within SEARCH_LINES)."""
    best = None
    for node in ast.walk(tree):
        if not _is_write_call(node):
            continue
        ln = getattr(node, "lineno", 0)
        if ln == line:
            if best is None or getattr(node, "col_offset", 0) < getattr(best, "col_offset", 0):
                best = node
    if best is not None:
        return best, "exact_line"
    for distance in range(1, SEARCH_LINES + 1):
        for node in ast.walk(tree):
            if not _is_write_call(node):
                continue
            ln = getattr(node, "lineno", 0)
            if abs(ln - line) == distance:
                if best is None or abs(ln - line) < abs(getattr(best, "lineno", 0) - line):
                    best = node
        if best is not None:
            return best, "near_line_%d" % distance
    return None, None


def write_call_paths(root, rel, line):
    """Fold the path argument of the write call recorded at ``rel:line``."""
    path = os.path.join(root, rel)
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return [], None, "the_source_is_larger_than_the_read_cap", "unknown"
        tree = ast.parse(e451.read_text(path))
    except (OSError, SyntaxError):
        return [], None, "the_source_cannot_be_parsed", "unknown"
    call, how = write_call_at(tree, line)
    if call is None:
        return [], None, None, None
    folder = FolderEx(rel, tree, root)
    names = dict(folder.module_bindings)
    names.update(folder.function_bindings(line))
    names.update(folder.for_bindings(line))
    arg = call.args[0] if call.args else None
    if arg is None:
        return [], call, "the_write_call_carries_no_positional_path_argument", how
    paths, unresolved = folder.fold(arg, names, 0)
    cleaned = []
    for p in paths:
        c = _clean(p)
        if c and c not in cleaned:
            cleaned.append(c)
    try:
        src = io.open(path, "r", encoding="utf-8", errors="replace").read()
        expression = (ast.get_source_segment(src, arg) or "").strip()[:200]
    except (OSError, SyntaxError):
        expression = ""
    return cleaned[:MAX_PATHS], {
        "callee": (call.func.id if isinstance(call.func, ast.Name) else
                   (call.func.attr if isinstance(call.func, ast.Attribute) else "")),
        "expression": expression,
        "unresolved": bool(unresolved),
    }, None, how


def wire_class_of(expected_paths, folded_paths, call_present, note):
    if not call_present:
        return W_NO_CALL
    if note is not None:
        return W_UNFOLDABLE
    expected = [_clean(p) for p in expected_paths if _clean(p)]
    folded = [_clean(p) for p in folded_paths if _clean(p)]
    if not folded:
        return W_UNFOLDABLE
    for p in folded:
        if p in expected:
            return W_WIRED
    for p in folded:
        for e in expected:
            if os.path.dirname(p) == os.path.dirname(e):
                return W_DIR_ONLY
    return W_ELSEWHERE


def classify(root=None, rows_input=None):
    rows_in, parent = rows_input if rows_input else population(root)
    rows = []
    for row in sorted(rows_in, key=lambda r: str(r.get("spelling"))):
        spelling = row.get("spelling")
        readers = [_clean(d) for d in (row.get("reader_directories")
                                       or row.get("resolved_directories") or [])]
        expected = ["%s/%s" % (d, spelling) for d in readers if d]
        sites = []
        notes = []
        for src in (row.get("tracing_sources") or [])[:MAX_SOURCES_PER_ROW]:
            rel = _norm(src.get("source"))
            line = src.get("line")
            if not rel or not line:
                continue
            paths, call, note, how = write_call_paths(root, rel, line)
            sites.append({
                "source": rel,
                "line": line,
                "route": src.get("route"),
                "call_found_at": how,
                "write_call": call,
                "folded_write_paths": paths,
                "note": note,
            })
            if note and note not in notes:
                notes.append(note)
        present = any(s.get("write_call") for s in sites)
        folds = [p for s in sites for p in (s.get("folded_write_paths") or [])]
        note = None
        if not present:
            note = "none"
        elif not folds:
            note = "no_fold"
        klass = wire_class_of(expected, folds, present, note)
        rows.append({
            "spelling": spelling,
            "stem": row.get("stem"),
            "expected_reader_paths": expected,
            "reader_directories": readers,
            "parent_route": row.get("parent_route"),
            "parent_directory_class": row.get("directory_class"),
            "write_sites": sites,
            "folded_write_paths": sorted({p for p in folds})[:MAX_PATHS],
            "wire_class": klass,
            "notes": notes,
        })
    return rows, parent


# ------------------------------------------------------------------ summary / verdict


def _recompute(face):
    rows = face.get("rows") or []
    counts = {k: 0 for k in CLASSES}
    for row in rows:
        if row.get("wire_class") in counts:
            counts[row["wire_class"]] += 1
    return {
        "population_spellings": len(rows),
        "population_write_sites": len({(s.get("source"), s.get("line")) for r in rows
                                       for s in (r.get("write_sites") or [])}),
        "wire_class_counts": counts,
        "spellings_whose_write_call_composes_the_reader_path": counts[W_WIRED],
        "spellings_whose_write_call_composes_the_reader_directory": (
            counts[W_WIRED] + counts[W_DIR_ONLY]),
        "spellings_whose_write_call_folds_elsewhere": counts[W_ELSEWHERE],
        "spellings_whose_write_call_cannot_be_folded": counts[W_UNFOLDABLE],
        "spellings_with_no_published_write_call": counts[W_NO_CALL],
    }


V_EMPTY = "the_parent_published_no_same_directory_spelling"
V_NONE = "no_same_directory_writer_write_call_composes_the_path_its_reader_opens"
V_ALL = "every_same_directory_writer_write_call_composes_the_path_its_reader_opens"
V_MOST = "most_same_directory_writer_write_calls_compose_the_path_their_reader_opens"
V_MINORITY = "a_minority_of_same_directory_writer_write_calls_compose_the_path_their_reader_opens"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST, V_MINORITY)


def _verdict(summary):
    total = int(summary.get("population_spellings") or 0)
    if not total:
        return V_EMPTY
    wired = int(summary.get("spellings_whose_write_call_composes_the_reader_path") or 0)
    if wired == 0:
        return V_NONE
    if wired == total:
        return V_ALL
    return V_MOST if wired * 2 >= total else V_MINORITY


# ------------------------------------------------------------------ build / write


def build(root=None, write=True):
    root = root or ROOT
    rows, parent = classify(root)
    summary = _recompute({"rows": rows})
    summary["parent_same_directory_spellings"] = parent["parent_same_directory_spellings"]
    summary["population_reproduced"] = parent["population_rows_agree_with_the_parent_tally"]
    face = {
        "card": CARD,
        "study": "E489_does_the_traced_write_call_join_the_very_constant_that_placed_"
                 "its_row_in_the_reader_directory",
        "title": "for the same-directory basename-only writers, does the write call's own path "
                 "expression compose the path the reader opens?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": parent,
        "fold_rule": {
            "constant": "a string constant is a path fragment",
            "name": "module, same-function and loop-target assignments fold up to %d hops"
                    % MAX_HOPS,
            "for": "a for-target binds to its iterable; a tuple/list iterable folds as "
                   "alternatives (the loop produces one of them)",
            "join": "os.path.join(a, b, ...) folds as the cartesian concatenation",
            "format": "'NAME-%s.json' % x is a format string, not a path, so it does not fold",
            "file": "os.path.dirname(...(os.path.abspath(__file__))) folds to the module "
                    "directory, walked up once per dirname wrapper",
            "call": "open/io.open/write_json/write_text first positional argument is the "
                    "write path",
        },
        "class_definition": {
            W_WIRED: "a folded write path equals <reader directory>/<spelling>",
            W_DIR_ONLY: "a folded write path has the reader's directory but another basename",
            W_ELSEWHERE: "the write call folds, and no path is in the reader's directory",
            W_UNFOLDABLE: "a write call is found at the site but its path argument folds to "
                          "nothing (parameter, argv, environment, format string)",
            W_NO_CALL: "no write call is found at or within %d lines of the recorded site"
                       % SEARCH_LINES,
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "the site is the line E487 traced; a write that happens in a helper called from "
            "that line is published as W_UNFOLDABLE rather than guessed",
            "a folded path is static: a name built from a function parameter, argv, env or a "
            "dict key does not fold, and the row is published as W_UNFOLDABLE, never as wired",
            "W_WIRED says the composed string equals the reader path; it does not claim the "
            "file exists at run time or that the write executes",
            "a %-format string is deliberately excluded from folding, so the dated-face arm of "
            "many writers contributes no path while the LATEST arm does",
            "the population is E488's same-directory arm kept byte-for-byte; this face adds a "
            "write-call question and does not re-open E487/E488's class questions",
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
        klass = row.get("wire_class")
        if klass not in CLASSES:
            problems.append("%s: unknown class %r" % (spelling, klass))
        sites = row.get("write_sites") or []
        present = any(s.get("write_call") for s in sites)
        folds = [p for s in sites for p in (s.get("folded_write_paths") or [])]
        note = None
        if not present:
            note = "none"
        elif not folds:
            note = "no_fold"
        expected = wire_class_of(row.get("expected_reader_paths") or [], folds, present, note)
        if klass != expected:
            problems.append("%s: class %r does not re-derive as %r" % (spelling, klass, expected))
        if row.get("parent_directory_class") != POPULATION_DIRECTORY_CLASS:
            problems.append("%s: row is not from the parent's same-directory arm" % (spelling,))
        if not row.get("expected_reader_paths"):
            problems.append("%s: a same-directory row publishes no reader path" % (spelling,))
    if _verdict({k: summary.get(k) for k in derived}) != face.get("verdict"):
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"),
                           _verdict({k: summary.get(k) for k in derived})))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e489 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    s = face.get("summary") or {}
    print("population=%d wired=%d dir_only=%d elsewhere=%d unfoldable=%d no_call=%d"
          % (s.get("population_spellings") or 0,
             s.get("spellings_whose_write_call_composes_the_reader_path") or 0,
             (s.get("wire_class_counts") or {}).get(W_DIR_ONLY, 0),
             s.get("spellings_whose_write_call_folds_elsewhere") or 0,
             s.get("spellings_whose_write_call_cannot_be_folded") or 0,
             s.get("spellings_with_no_published_write_call") or 0))
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
        if a[spelling].get("wire_class") != b[spelling].get("wire_class"):
            problems.append("%s: class moved %r -> %r" % (spelling,
                                                          a[spelling].get("wire_class"),
                                                          b[spelling].get("wire_class")))
    problems.extend(row_problems(fresh))
    print("e489 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir)
    os.makedirs(os.path.join(root, "scripts"))

    def row(spelling, source, line=10, directory="results/state_tilt"):
        return {"spelling": spelling, "stem": spelling.replace("_latest.json", ""),
                "parent_class": e487.C_DIRECT, "parent_route": "direct",
                "directory_class": POPULATION_DIRECTORY_CLASS,
                "resolved_directories": [directory],
                "tracing_sources": [{"source": source, "route": "direct", "line": line}]}

    rows = [
        row("wired_latest.json", "scripts/w_wired.py", 4),
        row("loop_latest.json", "scripts/w_loop.py", 6),
        row("other_latest.json", "scripts/w_other.py", 4),
        row("format_latest.json", "scripts/w_format.py", 3),
        row("nocall_latest.json", "scripts/w_nocall.py", 3),
    ]
    parent = {
        "verdict": e488.V_MOST,
        "evidence_cutoff": "2026-11-07",
        "summary": {"directory_class_counts": {POPULATION_DIRECTORY_CLASS: len(rows),
                                               e488.K_OTHER: 1}},
        "rows": rows + [{"spelling": "x_latest.json", "directory_class": e488.K_OTHER,
                         "resolved_directories": ["results/state_tilt"],
                         "tracing_sources": []}],
        "verdict_vocab": list(e488.VERDICT_VOCAB),
    }
    io.open(os.path.join(outdir, PARENT_FACE), "w", encoding="utf-8",
            newline="\n").write(json.dumps(parent))
    io.open(os.path.join(root, "scripts", "w_wired.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n"
        "with open(os.path.join(OUTDIR, 'wired_latest.json'), 'w') as fh:\n"
        "    fh.write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_loop.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n"
        "LATEST = 'loop_latest.json'\n"
        "for path in (OUTDIR + '/DATED.json', os.path.join(OUTDIR, LATEST)):\n"
        "    open(path, 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_other.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "OUTDIR = os.path.join(ROOT, 'results', 'quarantine')\n"
        "open(os.path.join(OUTDIR, 'other_latest.json'), 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_format.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import sys\n"
        "PATH = sys.argv[1]\n"
        "open(PATH, 'w').write('{}')\n")
    io.open(os.path.join(root, "scripts", "w_nocall.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n")
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e489_")
    root = _fixture(tmp)
    rows_in, parent = population(root)
    leg("the parent's same-directory arm is the population", len(rows_in) == 5)
    leg("the parent's tally is reproduced", parent["population_rows_agree_with_the_parent_tally"])
    leg("the parent count is carried", parent["parent_same_directory_spellings"] == 5)
    paths, call, note, how = write_call_paths(root, "scripts/w_wired.py", 4)
    leg("a direct write call folds to the reader path",
        paths == ["results/state_tilt/wired_latest.json"] and note is None)
    leg("the write call is located on its exact line", how == "exact_line")
    paths, call, note, how = write_call_paths(root, "scripts/w_loop.py", 6)
    leg("a loop variable over a tuple folds to both alternatives",
        "results/state_tilt/loop_latest.json" in paths)
    rows, _ = classify(root)
    by = {r["spelling"]: r for r in rows}
    leg("a direct compose is W_WIRED", by["wired_latest.json"]["wire_class"] == W_WIRED)
    leg("a loop variable is W_WIRED", by["loop_latest.json"]["wire_class"] == W_WIRED)
    leg("a quarantine write is W_ELSEWHERE",
        by["other_latest.json"]["wire_class"] == W_ELSEWHERE)
    leg("an argv path is W_UNFOLDABLE",
        by["format_latest.json"]["wire_class"] == W_UNFOLDABLE)
    leg("a module with no write call is W_NO_CALL",
        by["nocall_latest.json"]["wire_class"] == W_NO_CALL)
    leg("the class re-derives from published evidence",
        wire_class_of(by["wired_latest.json"]["expected_reader_paths"],
                      ["results/state_tilt/wired_latest.json"], True, None) == W_WIRED)
    leg("a same-directory other basename is W_DIR_ONLY",
        wire_class_of(["results/state_tilt/a_latest.json"],
                      ["results/state_tilt/b_latest.json"], True, None) == W_DIR_ONLY)
    leg("another directory is W_ELSEWHERE",
        wire_class_of(["results/state_tilt/a_latest.json"],
                      ["results/other/a_latest.json"], True, None) == W_ELSEWHERE)
    leg("no call is W_NO_CALL",
        wire_class_of(["results/state_tilt/a_latest.json"], [], False, "none") == W_NO_CALL)
    face = {"rows": rows, "evidence_cutoff": "2026-11-07"}
    summary = _recompute(face)
    face["summary"] = summary
    face["verdict"] = _verdict(summary)
    leg("the tallies re-derive", summary["population_spellings"] == len(rows))
    leg("every row lands in exactly one class",
        sum(summary["wire_class_counts"].values()) == len(rows))
    leg("the wired count is the headline",
        summary["spellings_whose_write_call_composes_the_reader_path"] == 2)
    leg("the fixture has no row problems", row_problems(face) == [])
    broken = json.loads(json.dumps(face))
    next(r for r in broken["rows"] if r["wire_class"] == W_WIRED)["wire_class"] = W_NO_CALL
    leg("a class that does not re-derive is refused", row_problems(broken))
    broken2 = json.loads(json.dumps(face))
    broken2["verdict"] = V_ALL
    leg("a verdict that does not re-derive is refused", row_problems(broken2))
    broken3 = json.loads(json.dumps(face))
    broken3["rows"][0]["expected_reader_paths"] = []
    leg("a row with no expected path is refused", row_problems(broken3))
    broken4 = json.loads(json.dumps(face))
    broken4["rows"][0]["parent_directory_class"] = e488.K_OTHER
    leg("a row outside the same-directory arm is refused", row_problems(broken4))
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
    print("e489 run verdict=%s" % face["verdict"])
    print("population=%d wired=%d dir_only=%d elsewhere=%d unfoldable=%d no_call=%d reproduced=%s"
          % (s["population_spellings"],
             s["spellings_whose_write_call_composes_the_reader_path"],
             (s["wire_class_counts"] or {}).get(W_DIR_ONLY, 0),
             s["spellings_whose_write_call_folds_elsewhere"],
             s["spellings_whose_write_call_cannot_be_folded"],
             s["spellings_with_no_published_write_call"],
             s.get("population_reproduced")))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E489 does the traced write call join the reader path")
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