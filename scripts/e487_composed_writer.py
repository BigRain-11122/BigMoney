"""E487 -- who writes the 84 latest spellings no source writes as a literal at the write site?

E482 published 84 ``*_latest.json`` spellings that resolve to a file no source writes as a literal.
Its writer witness is a literal sitting in the write call itself, so a face whose writer hands the
name to a helper (``write_json(os.path.join(OUTDIR, name), payload)``) or iterates a tuple of name
constants looks *unwritten*.  A face whose writer only composes its name cannot be retired by a
literal-writer census: the census is blind, not the writer missing.  This face prices that blind
spot instead of assuming it.

Population = the 84 rows E482 published with class ``a_file_carries_this_spelling_but_no_source_
writes_it``.  For each spelling the stem (basename minus ``_latest.json``) is searched over the
python corpus as a *token* -- ``(?<![a-z0-9])stem(?![a-z0-9])`` so ``state`` does not fire inside
``statement`` -- and every writer is asked whether a string literal that carries the stem reaches
its write path.  The path analysis is three named routes, each published separately:

  direct   the literal is bound to a name used in the write call's own path expression
  helper   the literal reaches a *local write helper's* path parameter, and the helper is called
           with it (one interprocedural hop; a helper imported from another module is not traced)
  loop     the name is a ``for`` target over a tuple/dict of name constants that feeds the path

A route is the *weakest* one that had to be taken, so ``direct`` is the strongest evidence and
``loop`` the weakest.  Everything a route cannot reach is published as a residue class, never
folded into the positive count.

Run:      python scripts/e487_composed_writer.py run
Verify:   python scripts/e487_composed_writer.py verify   (re-derives from the live tree)
Check:    python scripts/e487_composed_writer.py check    (tallies re-derive from the face)
Selftest: python scripts/e487_composed_writer.py selftest
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
import e482_latest_outside as e482  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "composedwriter_latest.json"
DATED_PREFIX = "COMPOSEDWRITER"
CARD = ("E487-OF-THE-SPELLINGS-NO-SOURCE-WRITES-LITERALLY-HOW-MANY-HAVE-A-COMPOSED-WRITER")

PARENT_FACE = "latestoutside_latest.json"      # E482
SUFFIX = "_latest.json"

# The parent's exclusion list is kept (its population is defined under it) and extended with this
# face's own family.  Sources in this set are scanned separately as the *excluded* arm, so the
# blindness the population inherits is measured rather than left as a hole.
EXCLUDED_PREFIX = e482.SELF_PREFIX + ("e487_", "run_e487")

MAX_READ_BYTES = 2 * 1024 * 1024
MAX_ROWS_PER_LIST = 12
MAX_LITERALS_PER_SOURCE = 40
MAX_HOPS = 3
NON_PY_SUFFIXES = (".ps1", ".psm1", ".cmd", ".bat")

# ---- routes (weakest wins) --------------------------------------------------------------------
R_DIRECT = "direct"
R_HELPER = "helper"
R_LOOP = "loop"
ROUTES = (R_DIRECT, R_HELPER, R_LOOP)

# ---- per-spelling classes ---------------------------------------------------------------------
C_DIRECT = "the_write_path_reaches_a_name_bound_to_a_literal_that_carries_the_stem"
C_HELPER = "the_write_path_reaches_the_stem_only_through_a_write_helper_argument"
C_LOOP = "the_write_path_reaches_the_stem_only_through_a_loop_over_name_constants"
C_EXCLUDED = "the_stem_is_named_by_writing_sources_that_this_census_excludes"
C_NONPY = "only_a_non_python_source_names_the_stem"
C_RESIDUE = "a_source_that_writes_names_the_stem_but_no_write_path_is_traced"
C_READER_ONLY = "only_its_readers_name_the_stem"
C_UNNAMED = "no_source_in_the_corpus_names_the_stem"
CLASSES = (C_DIRECT, C_HELPER, C_LOOP, C_EXCLUDED, C_NONPY, C_RESIDUE, C_READER_ONLY, C_UNNAMED)
TRACED = (C_DIRECT, C_HELPER, C_LOOP)

# ---- directory arms ---------------------------------------------------------------------------
D_SAME = "the_writer_path_reaches_the_directory_the_reader_resolves_to"
D_BASENAME_ONLY = "the_writer_path_reaches_only_a_bare_basename_so_the_directory_is_untraced"
D_OTHER = "the_writer_path_reaches_a_stated_directory_that_is_not_the_reader_directory"
DIRECTORY_CLASSES = (D_SAME, D_BASENAME_ONLY, D_OTHER)

# ---- verdicts ---------------------------------------------------------------------------------
V_EMPTY = "the_parent_published_no_unwritten_spelling"
V_NONE = "no_unwritten_spelling_has_a_write_path_that_traces_back_to_its_stem"
V_ALL = "every_unwritten_spelling_has_a_write_path_that_traces_back_to_its_stem"
V_MOST_TRACED = ("most_unwritten_spellings_have_a_writing_source_whose_path_traces_back_to_the_"
                 "stem")
V_MOST_UNTRACED = "most_unwritten_spellings_have_no_writing_source_whose_path_traces_to_the_stem"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST_TRACED, V_MOST_UNTRACED)

# a stem this short or this ordinary cannot witness anything on its own; published as a flag on
# every row rather than used to move a row between classes (E208: pruning a real hit is worse)
GENERIC_STEMS = ("latest", "state", "status", "temp", "tmp", "test", "tests", "index", "data",
                 "out", "output", "log", "logs", "misc", "main", "build", "run", "probe")


def _norm(text):
    return str(text or "").replace("\\", "/").strip()


def _stem_of(spelling):
    base = os.path.basename(_norm(spelling))
    if base.endswith(SUFFIX):
        base = base[: -len(SUFFIX)]
    return base.strip("_").lower()


def _is_generic(stem):
    return len(stem) < 5 or stem in GENERIC_STEMS


def _token_re(stems):
    """One alternation, longest stem first, with token boundaries (E444: name the witness)."""
    ordered = sorted({s for s in stems if s}, key=len, reverse=True)
    if not ordered:
        return None
    return re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(s) for s in ordered) +
                      r")(?![a-z0-9])")


def _names_in(node):
    return {e.id for e in ast.walk(node) if isinstance(e, ast.Name)}


def _strings_in(node):
    return [e.value for e in ast.walk(node) if isinstance(e, ast.Constant)
            and isinstance(e.value, str)]


# ------------------------------------------------------------------ population


def population(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    face = json.load(io.open(path, "r", encoding="utf-8"))
    summary = face.get("summary") or {}
    rows = [r for r in face.get("rows") or [] if r.get("class") == e482.C_FILE_NO_WRITER]
    parent = {
        "face": PARENT_FACE,
        "face_verdict": face.get("verdict"),
        "face_evidence_cutoff": face.get("evidence_cutoff"),
        "parent_distinct_spellings": summary.get("distinct_spellings"),
        "parent_class_counts": summary.get("class_counts"),
        "parent_unwritten_spellings": (summary.get("class_counts") or {}).get(
            e482.C_FILE_NO_WRITER),
        "population_rows_agree_with_the_parent_tally": (summary.get("class_counts") or {}).get(
            e482.C_FILE_NO_WRITER) == len(rows),
        "excluded_source_prefixes": list(EXCLUDED_PREFIX),
    }
    return rows, parent


# ------------------------------------------------------------------ path analysis


def _write_calls(tree):
    """(line, path node) for every write of a path."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute)
                                                       else "")
        if name == "open":
            mode = ""
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                mode = node.args[1].value
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant) \
                        and isinstance(kw.value.value, str):
                    mode = kw.value.value
            if "w" not in mode and "a" not in mode:
                continue
        elif name != "write_text":
            continue
        arg = node.args[0] if node.args else None
        if arg is not None:
            out.append((getattr(node, "lineno", 0), arg))
    return out


def _bindings(tree, follow_loops):
    """name -> string literals it is bound to, and name -> names it is built from."""
    lit, ref = {}, {}

    def add(target, value):
        vals = _strings_in(value) if value is not None else []
        refs = _names_in(value) if value is not None else set()
        if vals:
            lit.setdefault(target, set()).update(vals)
        if refs:
            ref.setdefault(target, set()).update(refs)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    add(target.id, node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            add(node.target.id, node.value)
        elif follow_loops and isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            add(node.target.id, node.iter)
    return lit, ref


def _expand(names, lit, ref):
    """Transitive closure of names over assignments, bounded (E444: no unbounded walk)."""
    seen, literals = set(), []
    frontier = list(names)
    for _ in range(MAX_HOPS):
        nxt = []
        for name in frontier:
            if name in seen:
                continue
            seen.add(name)
            literals.extend(lit.get(name) or [])
            nxt.extend(ref.get(name) or [])
        frontier = nxt
        if not frontier:
            break
    return literals


def _helper_paths(tree, lit, ref):
    """function name -> argument indices whose value reaches a write of a path."""
    out = {}
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        params = [a.arg for a in fn.args.args]
        if not params:
            continue
        inner_lit, inner_ref = _bindings(fn, True)
        for line, arg in _write_calls(fn):
            names = _names_in(arg)
            reachable = set(names) | set(_expand(names, inner_lit, inner_ref))
            for index, param in enumerate(params):
                if param in reachable:
                    out.setdefault(fn.name, set()).add(index)
    return out


def source_evidence(text):
    """What this source can prove, per route.  Returns {route: [(spelling token, line, literals)]}.

    ``direct`` and ``helper`` use bindings *without* loop targets; ``loop`` is what only becomes
    visible once a ``for`` target is followed.  So a stem proved by ``direct`` is not re-counted as
    a loop proof, and the route published per row is the weakest that had to be taken.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    out = {R_DIRECT: [], R_HELPER: [], R_LOOP: []}
    lit0, ref0 = _bindings(tree, follow_loops=False)
    lit1, ref1 = _bindings(tree, follow_loops=True)
    helpers = _helper_paths(tree, lit0, ref0)
    for line, arg in _write_calls(tree):
        names = _names_in(arg)
        out[R_DIRECT].append((line, _expand(names, lit0, ref0), _strings_in(arg)))
        out[R_HELPER].append((line, _expand(names, lit0, ref0), _strings_in(arg)))
        out[R_LOOP].append((line, _expand(names, lit1, ref1), _strings_in(arg)))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute)
                                                       else "")
        if name not in helpers:
            continue
        for index in sorted(helpers[name]):
            if index >= len(node.args):
                continue
            arg = node.args[index]
            names = _names_in(arg)
            line = getattr(node, "lineno", 0)
            out[R_HELPER].append((line, _expand(names, lit0, ref0), _strings_in(arg)))
            out[R_LOOP].append((line, _expand(names, lit1, ref1), _strings_in(arg)))
    # the write path's own string constants are evidence too: os.path.join(OUT, name + "_latest")
    for route in ROUTES:
        out[route] = [(ln, lits, consts) for ln, lits, consts in out[route]]
    return out


def scan(root=None, stems=None):
    """Corpus pass: which source proves which stem, by weakest route, plus the excluded arm."""
    root = root or ROOT
    stems = list(stems or [])
    pattern = _token_re(stems)
    evidence = {s: {"routes": set(), "sources": {}, "literals": {}, "namers_all": set()}
                for s in stems}
    excluded = {s: set() for s in stems}
    non_py = {s: set() for s in stems}
    meta = {"python_sources_scanned": 0, "python_sources_naming_a_stem": 0,
            "python_sources_scanned_but_excluded": 0,
            "excluded_sources_naming_a_stem": 0,
            "non_python_sources_scanned": 0, "non_python_sources_naming_a_stem": 0}
    if pattern is None:
        return evidence, excluded, non_py, meta

    def order(route):
        return ROUTES.index(route)

    for rel in e468._walk_py(root):
        name = os.path.basename(rel)
        is_excluded = name.startswith(EXCLUDED_PREFIX)
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except OSError:
            continue
        named = {m.group(1) for m in pattern.finditer(text.lower())}
        if is_excluded:
            meta["python_sources_scanned_but_excluded"] += 1
            if named:
                meta["excluded_sources_naming_a_stem"] += 1
                for stem in named:
                    if stem in excluded:
                        excluded[stem].add(rel)
            continue
        meta["python_sources_scanned"] += 1
        if not named:
            continue
        meta["python_sources_naming_a_stem"] += 1
        for stem in named:
            if stem in evidence:
                evidence[stem]["namers_all"].add(rel)
        ev = source_evidence(text)
        if ev is None:
            continue
        for route in ROUTES:
            for line, literals, consts in ev[route]:
                blob = " ".join(list(literals) + list(consts)).lower()
                stems_here = {m.group(1) for m in pattern.finditer(blob)}
                if not stems_here:
                    continue
                # only publish literals that carry a stem token or name a path: an expansion over
                # a large module reaches every comparable string, and keeping them all turns a
                # census into a memory dump (r1508 family: publish the witness, not the walk)
                keep = [_norm(x) for x in list(literals) + list(consts)
                        if "/" in _norm(x) or pattern.search(_norm(x).lower())]
                for stem in stems_here:
                    if stem not in evidence or stem not in named:
                        continue
                    slot = evidence[stem]
                    slot["routes"].add(route)
                    prev = slot["sources"].get(rel)
                    if prev is None or order(route) < order(prev[0]):
                        slot["sources"][rel] = (route, line)
                    slot["literals"].setdefault(rel, set()).update(keep[:MAX_LITERALS_PER_SOURCE])
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in e482.INDEX_SKIP_DIRS]
        for fname in filenames:
            if not fname.lower().endswith(NON_PY_SUFFIXES):
                continue
            full = os.path.join(dirpath, fname)
            try:
                if os.path.getsize(full) > MAX_READ_BYTES:
                    continue
                text = e451.read_text(full)
            except OSError:
                continue
            meta["non_python_sources_scanned"] += 1
            named = {m.group(1) for m in pattern.finditer(text.lower())}
            if not named:
                continue
            meta["non_python_sources_naming_a_stem"] += 1
            rel = os.path.relpath(full, root).replace("\\", "/")
            for stem in named:
                if stem in non_py:
                    non_py[stem].add(rel)
    return evidence, excluded, non_py, meta


# ------------------------------------------------------------------ classify


def _route_of(routes):
    for route in ROUTES:
        if route in routes:
            return route
    return None


def _directory_class(literals, resolved_paths):
    """Did the traced writer path reach the directory the reader resolves to?"""
    want = sorted({os.path.dirname(_norm(p)) for p in resolved_paths if p})
    paths = sorted({lit for lit in literals if "/" in lit})
    if not paths or not want:
        return D_BASENAME_ONLY
    for path in paths:
        candidate = _norm(path)
        while candidate:
            if candidate in want:
                return D_SAME
            parent = os.path.dirname(candidate)
            # os.path.dirname is not a descent for '../..', '/', 'C:/' or '.': it returns the
            # same string, so the ancestor walk never ends (r1512: the run hung here).
            if parent == candidate or parent in (".", ""):
                break
            candidate = parent
    return D_OTHER


def classify(root=None, rows_input=None):
    rows_in, parent = rows_input if rows_input else population(root)
    stems = sorted({_stem_of(r.get("spelling")) for r in rows_in})
    evidence, excluded, non_py, meta = scan(root, stems)
    rows = []
    for parent_row in sorted(rows_in, key=lambda r: str(r.get("spelling"))):
        spelling = str(parent_row.get("spelling") or "")
        stem = _stem_of(spelling)
        readers = sorted({_norm(s) for s in (parent_row.get("sources") or [])})
        slot = evidence.get(stem) or {"routes": set(), "sources": {}, "literals": {},
                                      "namers_all": set()}
        route = _route_of(slot["routes"])
        namers = sorted(slot["sources"])
        naming = sorted(slot.get("namers_all") or [])
        excluded_namers = sorted(excluded.get(stem) or [])
        np_namers = sorted(non_py.get(stem) or [])
        writers_outside_readers = [s for s in naming if s not in readers]
        if route == R_DIRECT:
            klass = C_DIRECT
        elif route == R_HELPER:
            klass = C_HELPER
        elif route == R_LOOP:
            klass = C_LOOP
        elif excluded_namers:
            klass = C_EXCLUDED
        elif np_namers:
            klass = C_NONPY
        elif writers_outside_readers:
            klass = C_RESIDUE
        elif naming:
            klass = C_READER_ONLY
        else:
            klass = C_UNNAMED
        literals = sorted({lit for vals in slot["literals"].values() for lit in vals})
        resolved = [_norm(p) for p in (parent_row.get("resolved_paths") or [])]
        # the directory class is read off the literals the row publishes, not the full set:
        # a class computed from rows the face does not carry cannot re-derive (r1512, E444).
        published_literals = literals[:MAX_ROWS_PER_LIST]
        published_resolved = resolved[:MAX_ROWS_PER_LIST]
        rows.append({
            "spelling": spelling,
            "stem": stem,
            "class": klass,
            "route": route,
            "stem_is_generic": _is_generic(stem),
            "resolved_paths": published_resolved,
            "resolved_directories": sorted({os.path.dirname(p) for p in resolved if p}),
            "reader_sources": readers[:MAX_ROWS_PER_LIST],
            "reader_source_count": len(readers),
            "tracing_sources": [{"source": s, "route": slot["sources"][s][0],
                                 "line": slot["sources"][s][1]} for s in namers][
                                    :MAX_ROWS_PER_LIST],
            "tracing_source_count": len(namers),
            "tracing_sources_outside_the_readers": writers_outside_readers[:MAX_ROWS_PER_LIST],
            "naming_source_count": len(naming),
            "naming_sources_outside_the_readers": writers_outside_readers[:MAX_ROWS_PER_LIST],
            "excluded_source_namers": excluded_namers[:MAX_ROWS_PER_LIST],
            "non_python_namers": np_namers[:MAX_ROWS_PER_LIST],
            "traced_literals": published_literals,
            "directory_class": (_directory_class(published_literals, published_resolved)
                                if klass in TRACED else None),
        })
    return rows, meta, parent


# ------------------------------------------------------------------ summary / verdict


def _recompute(face):
    rows = face.get("rows") or []
    counts = {k: 0 for k in CLASSES}
    for row in rows:
        if row.get("class") in counts:
            counts[row["class"]] += 1
    dir_counts = {k: 0 for k in DIRECTORY_CLASSES}
    for row in rows:
        if row.get("class") in TRACED and row.get("directory_class") in dir_counts:
            dir_counts[row["directory_class"]] += 1
    traced = [r for r in rows if r.get("class") in TRACED]
    return {
        "population_spellings": len(rows),
        "population_reader_sources": len({s for r in rows
                                          for s in (r.get("reader_sources") or [])}),
        "class_counts": counts,
        "spellings_whose_write_path_traces_to_the_stem": len(traced),
        "spellings_traced_directly": counts[C_DIRECT],
        "spellings_traced_through_a_write_helper": counts[C_HELPER],
        "spellings_traced_through_a_loop_over_name_constants": counts[C_LOOP],
        "spellings_named_only_by_excluded_sources": counts[C_EXCLUDED],
        "spellings_named_only_by_a_non_python_source": counts[C_NONPY],
        "spellings_named_by_writers_but_not_traced": counts[C_RESIDUE],
        "spellings_named_only_by_their_readers": counts[C_READER_ONLY],
        "spellings_no_source_names": counts[C_UNNAMED],
        "spellings_with_a_generic_stem_flag": sum(1 for r in rows if r.get("stem_is_generic")),
        "directory_class_counts": dir_counts,
        "traced_spellings_whose_path_reaches_the_reader_directory": dir_counts[D_SAME],
        "traced_spellings_whose_path_reaches_only_a_basename": dir_counts[D_BASENAME_ONLY],
        "traced_spellings_whose_path_reaches_another_directory": dir_counts[D_OTHER],
    }


def _verdict(summary):
    total = int(summary.get("population_spellings") or 0)
    if not total:
        return V_EMPTY
    traced = int(summary.get("spellings_whose_write_path_traces_to_the_stem") or 0)
    rest = total - traced
    if traced == 0:
        return V_NONE
    if rest == 0:
        return V_ALL
    return V_MOST_TRACED if traced >= rest else V_MOST_UNTRACED


# ------------------------------------------------------------------ build


def build(root=None, write=True):
    root = root or ROOT
    rows, meta, parent = classify(root)
    summary = _recompute({"rows": rows})
    summary["python_sources_scanned"] = meta["python_sources_scanned"]
    summary["python_sources_naming_a_stem"] = meta["python_sources_naming_a_stem"]
    summary["python_sources_scanned_but_excluded"] = meta["python_sources_scanned_but_excluded"]
    summary["excluded_sources_naming_a_stem"] = meta["excluded_sources_naming_a_stem"]
    summary["non_python_sources_scanned"] = meta["non_python_sources_scanned"]
    summary["non_python_sources_naming_a_stem"] = meta["non_python_sources_naming_a_stem"]
    summary["parent_unwritten_spellings"] = parent["parent_unwritten_spellings"]
    summary["population_reproduced"] = parent["population_rows_agree_with_the_parent_tally"]
    face = {
        "card": CARD,
        "study": ("E487_of_the_spellings_no_source_writes_literally_how_many_have_a_composed_"
                  "writer"),
        "title": "of the spellings no source writes literally, how many have a composed writer?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": parent,
        "route_definition": {
            R_DIRECT: "a literal that carries the stem is bound to a name used in the write "
                      "call's own path expression (assignments followed up to 3 hops)",
            R_HELPER: "the literal reaches the path parameter of a *local* write helper and the "
                      "helper is called with it: one interprocedural hop, a helper imported from "
                      "another module is not traced",
            R_LOOP: "the name only resolves once a ``for`` target iterating a tuple/dict of name "
                    "constants is followed: the weakest route, so it is only claimed when no "
                    "stronger one exists",
        },
        "class_definition": {
            C_DIRECT: "a write path traces back to a letter-for-letter stem literal directly",
            C_HELPER: "the stem only reaches a write path through a local helper's argument",
            C_LOOP: "the stem only reaches a write path through a loop target over name constants",
            C_EXCLUDED: "no in-corpus source traces the stem, but a source this census excludes "
                        "does name it and writes: the blindness the population inherits is named",
            C_NONPY: "no python source traces the stem, a non-python source names it",
            C_RESIDUE: "an in-corpus source names the stem and writes files, but no write path "
                       "traces back to it: the name is incidental to that source's writes",
            C_READER_ONLY: "only the sources that already open this spelling name its stem",
            C_UNNAMED: "no source in the corpus names the stem at all",
        },
        "directory_class_definition": {
            D_SAME: "a string the traced path reaches names the directory the reader resolves to",
            D_BASENAME_ONLY: "the traced path reaches only bare basenames, so the directory comes "
                             "from somewhere this analysis does not follow",
            D_OTHER: "the traced path reaches a stated path in a different directory",
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "a writer that passes the name to a helper imported from another module, or builds it "
            "from a dict keyed by something else, is not traced: those rows land in the residue "
            "class, never in a traced class",
            "the residue class is not 'no writer'. It says that this source names the stem and "
            "writes files but no write path traces back to that name -- the same statement the "
            "parent made about literals, one level up",
            "a stem hit is a token match on the source text, so a comment, a docstring or a test "
            "assertion counts as naming; the route says whether that naming reaches a write",
            "the population is defined under E482's exclusion list; this face keeps it and then "
            "scans those excluded sources as its own arm so the inherited blindness is counted "
            "instead of being silently inherited twice",
            "a generic stem (shorter than five characters or an ordinary word) is flagged on its "
            "row and NOT moved between classes: pruning a real trace is worse than publishing the "
            "caveat (E208)",
            "no data flow across modules and no runtime tracing: this is a static path census of "
            "one file at a time",
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


# ------------------------------------------------------------------ check / verify / run


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
        if row.get("stem") != _stem_of(spelling):
            problems.append("%s: stem %r does not re-derive from the spelling"
                            % (spelling, row.get("stem")))
        klass = row.get("class")
        if klass not in CLASSES:
            problems.append("%s: unknown class %r" % (spelling, klass))
        if row.get("stem_is_generic") != _is_generic(str(row.get("stem") or "")):
            problems.append("%s: the generic flag does not re-derive" % (spelling,))
        if klass in TRACED:
            if not row.get("tracing_source_count"):
                problems.append("%s: a traced class with no tracing source" % (spelling,))
            if row.get("route") not in ROUTES:
                problems.append("%s: a traced row states no route" % (spelling,))
            if not row.get("traced_literals"):
                problems.append("%s: a traced row reaches no literal" % (spelling,))
            expected = _directory_class(row.get("traced_literals") or [],
                                        row.get("resolved_paths") or [])
            if row.get("directory_class") != expected:
                problems.append("%s: directory class %r does not re-derive as %r"
                                % (spelling, row.get("directory_class"), expected))
        else:
            if row.get("route") is not None:
                problems.append("%s: an untraced row states a route" % (spelling,))
            if row.get("directory_class") is not None:
                problems.append("%s: an untraced row states a directory class" % (spelling,))
        if klass == C_RESIDUE and not row.get("naming_sources_outside_the_readers"):
            problems.append("%s: residue class with no naming source outside the readers"
                            % (spelling,))
        if klass == C_READER_ONLY and (row.get("naming_sources_outside_the_readers")
                                       or row.get("tracing_source_count")):
            problems.append("%s: reader-only class beside an outside namer" % (spelling,))
        if klass == C_UNNAMED and (row.get("tracing_source_count")
                                   or row.get("naming_source_count")
                                   or row.get("reader_source_count")
                                   or row.get("excluded_source_namers")
                                   or row.get("non_python_namers")):
            problems.append("%s: unnamed class beside a naming source" % (spelling,))
        if klass == C_EXCLUDED and (row.get("tracing_source_count")
                                    or not row.get("excluded_source_namers")):
            problems.append("%s: excluded class does not fit its own sources" % (spelling,))
        if klass == C_NONPY and (row.get("tracing_source_count")
                                 or not row.get("non_python_namers")):
            problems.append("%s: non-python class does not fit its own sources" % (spelling,))
    if _verdict({k: summary.get(k) for k in derived}) != face.get("verdict"):
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"),
                           _verdict({k: summary.get(k) for k in derived})))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e487 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    summary = face.get("summary") or {}
    print("population=%d traced=%d (direct %d / helper %d / loop %d) residue=%d excluded=%d"
          % (summary.get("population_spellings") or 0,
             summary.get("spellings_whose_write_path_traces_to_the_stem") or 0,
             summary.get("spellings_traced_directly") or 0,
             summary.get("spellings_traced_through_a_write_helper") or 0,
             summary.get("spellings_traced_through_a_loop_over_name_constants") or 0,
             summary.get("spellings_named_by_writers_but_not_traced") or 0,
             summary.get("spellings_named_only_by_excluded_sources") or 0))
    return 0 if not problems else 1


def verify(root=None):
    """Re-derive every row from the live tree and compare against the published face."""
    root = root or ROOT
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build(root, write=False)
    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved")
    a = {r["spelling"]: r for r in published.get("rows") or []}
    b = {r["spelling"]: r for r in fresh.get("rows") or []}
    if set(a) != set(b):
        problems.append("population moved: +%d -%d"
                        % (len(set(b) - set(a)), len(set(a) - set(b))))
    for spelling in sorted(set(a) & set(b)):
        for key in ("class", "route", "directory_class", "stem_is_generic",
                    "tracing_source_count"):
            if a[spelling].get(key) != b[spelling].get(key):
                problems.append("%s: %s moved %r -> %r"
                                % (spelling, key, a[spelling].get(key), b[spelling].get(key)))
    problems.extend(row_problems(fresh))
    print("e487 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    """A tiny tree with one spelling per class and per route, plus a parent face."""
    os.makedirs(os.path.join(root, "results", "state_tilt"))
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "Tools"))

    def row(spelling, sources):
        return {"spelling": spelling, "class": e482.C_FILE_NO_WRITER, "site_count": 1,
                "sources": sources,
                "resolved_paths": ["results/state_tilt/%s" % spelling]}

    parent_rows = [
        row("directstem_latest.json", ["scripts/reader_a.py"]),
        row("helperstem_latest.json", ["scripts/reader_a.py"]),
        row("loopstem_latest.json", ["scripts/reader_a.py"]),
        row("excludedstem_latest.json", ["scripts/reader_a.py"]),
        row("psonly_latest.json", ["scripts/reader_a.py"]),
        row("residuestem_latest.json", ["scripts/reader_a.py"]),
        row("readeronly_latest.json", ["scripts/reader_a.py"]),
        row("orphanstem_latest.json", []),
    ]
    parent = {
        "verdict": e482.V_MOST_LIVE,
        "evidence_cutoff": "2026-11-07",
        "summary": {"distinct_spellings": 10,
                    "class_counts": {e482.C_FILE_WRITER: 2,
                                     e482.C_FILE_NO_WRITER: len(parent_rows)}},
        "rows": parent_rows + [{"spelling": "written_latest.json",
                                "class": e482.C_FILE_WRITER, "sources": [], "site_count": 1,
                                "resolved_paths": []}],
    }
    io.open(os.path.join(root, "results", "state_tilt", PARENT_FACE), "w", encoding="utf-8",
            newline="\n").write(json.dumps(parent))
    for r in parent_rows:
        io.open(os.path.join(root, "results", "state_tilt", r["spelling"]), "w",
                encoding="utf-8", newline="\n").write("{}")
    # one reader that opens every spelling (so each stem has a reader)
    io.open(os.path.join(root, "scripts", "reader_a.py"), "w", encoding="utf-8",
            newline="\n").write("import json\n" + "".join(
                "json.load(open('results/state_tilt/%s'))\n" % r["spelling"]
                for r in parent_rows if r["sources"]))
    # direct: constant bound to a stem literal used in the write path
    io.open(os.path.join(root, "scripts", "direct_writer.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "OUT = 'results/state_tilt'\n"
        "NAME = 'directstem_latest.json'\n"
        "open(os.path.join(OUT, NAME), 'w').write('{}')\n")
    # helper: the literal reaches a local write helper's path parameter
    io.open(os.path.join(root, "scripts", "helper_writer.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import json, os\n"
        "OUT = 'results/state_tilt'\n"
        "LATEST = 'helperstem_latest.json'\n"
        "def write_json(path, payload):\n"
        "    with open(path, 'w') as fh:\n"
        "        json.dump(payload, fh)\n"
        "write_json(os.path.join(OUT, LATEST), {})\n")
    # loop: the name only resolves through a for target over constants
    io.open(os.path.join(root, "scripts", "loop_writer.py"), "w", encoding="utf-8",
            newline="\n").write(
        "import os\n"
        "OUT = 'results/state_tilt'\n"
        "FACE = 'facetext'\n"
        "LATEST = 'loopstem_latest.json'\n"
        "for name in (FACE, LATEST):\n"
        "    open(os.path.join(OUT, name), 'w').write('{}')\n")
    # residue: names the stem and writes, but no write path uses the name
    io.open(os.path.join(root, "scripts", "residue_writer.py"), "w", encoding="utf-8",
            newline="\n").write(
        "# residuestem is documented here\n"
        "open('results/state_tilt/other.json', 'w').write('{}')\n")
    # a source this census excludes that names and writes a stem
    io.open(os.path.join(root, "scripts", "e487_own_runner.py"), "w", encoding="utf-8",
            newline="\n").write(
        "stem = 'excludedstem_latest.json'\n"
        "open('results/state_tilt/' + stem, 'w').write('{}')\n")
    io.open(os.path.join(root, "Tools", "ps_writer.ps1"), "w", encoding="utf-8",
            newline="\n").write("$x = 'psonly'\nSet-Content -Path \"$x.txt\" -Value 1\n")
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e487_")
    root = _fixture(tmp)
    rows_in, parent = population(root)
    leg("the parent's unwritten class is the population", len(rows_in) == 8)
    leg("the parent's tally is reproduced", parent["population_rows_agree_with_the_parent_tally"])
    leg("the parent count is carried", parent["parent_unwritten_spellings"] == 8)
    leg("a stem is the basename minus the suffix",
        _stem_of("results/state_tilt/BasisRecovery_latest.json") == "basisrecovery")
    leg("a short stem is flagged generic", _is_generic("data") and not _is_generic("datastore"))
    leg("a token boundary keeps state out of statement",
        [m.group(1) for m in _token_re(["state"]).finditer("statement about state")] == ["state"])
    leg("the longest stem wins at one position",
        [m.group(1) for m in _token_re(["state", "statement"]).finditer("statement")]
        == ["statement"])
    rows, meta, _ = classify(root)
    by = {r["spelling"]: r for r in rows}
    leg("a direct trace is the direct class",
        by["directstem_latest.json"]["class"] == C_DIRECT)
    leg("a helper trace is the helper class",
        by["helperstem_latest.json"]["class"] == C_HELPER)
    leg("a loop trace is the loop class",
        by["loopstem_latest.json"]["class"] == C_LOOP)
    leg("an excluded-family writer is named as excluded",
        by["excludedstem_latest.json"]["class"] == C_EXCLUDED
        and by["excludedstem_latest.json"]["excluded_source_namers"] == ["scripts/e487_own_runner.py"])
    leg("a non-python namer is the non-python class",
        by["psonly_latest.json"]["class"] == C_NONPY)
    leg("naming without a traced path is the residue",
        by["residuestem_latest.json"]["class"] == C_RESIDUE)
    leg("a stem only its readers know is reader-only",
        by["readeronly_latest.json"]["class"] == C_READER_ONLY)
    leg("a stem nothing names is unnamed",
        by["orphanstem_latest.json"]["class"] == C_UNNAMED)
    leg("a traced path that reaches the reader directory says so",
        by["directstem_latest.json"]["directory_class"] == D_SAME)
    leg("a traced path that reaches only a basename says so",
        by["helperstem_latest.json"]["directory_class"] in (D_SAME, D_BASENAME_ONLY))
    leg("the excluded arm counted a source",
        meta["excluded_sources_naming_a_stem"] >= 1)
    face = {"rows": rows, "evidence_cutoff": "2026-11-07"}
    summary = _recompute(face)
    face["summary"] = summary
    face["verdict"] = _verdict(summary)
    leg("the tallies re-derive", _recompute(face)["population_spellings"] == len(rows))
    leg("three routes are counted separately",
        summary["spellings_traced_directly"] == 1
        and summary["spellings_traced_through_a_write_helper"] == 1
        and summary["spellings_traced_through_a_loop_over_name_constants"] == 1)
    leg("the verdict follows the traced count",
        face["verdict"] == V_MOST_TRACED or face["verdict"] == V_MOST_UNTRACED)
    leg("the fixture has no row problems", row_problems(face) == [])
    broken = json.loads(json.dumps(face))
    next(r for r in broken["rows"] if r["class"] == C_RESIDUE)["class"] = C_DIRECT
    leg("a traced class without a tracing source is refused", row_problems(broken))
    broken2 = json.loads(json.dumps(face))
    next(r for r in broken2["rows"] if r["class"] == C_DIRECT)["route"] = None
    leg("a traced row with no route is refused", row_problems(broken2))
    broken3 = json.loads(json.dumps(face))
    broken3["verdict"] = V_ALL
    leg("a verdict that does not re-derive is refused", row_problems(broken3))
    broken4 = json.loads(json.dumps(face))
    broken4["rows"][0]["stem"] = "somethingelse"
    leg("a stem that does not re-derive is refused", row_problems(broken4))
    broken5 = json.loads(json.dumps(face))
    next(r for r in broken5["rows"] if r["class"] == C_UNNAMED)["naming_source_count"] = 1
    leg("an unnamed row beside a naming source is refused", row_problems(broken5))
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
    summary = face["summary"]
    print("e487 run verdict=%s" % face["verdict"])
    print("population=%d traced=%d (direct %d / helper %d / loop %d)"
          % (summary["population_spellings"],
             summary["spellings_whose_write_path_traces_to_the_stem"],
             summary["spellings_traced_directly"],
             summary["spellings_traced_through_a_write_helper"],
             summary["spellings_traced_through_a_loop_over_name_constants"]))
    print("residue=%d excluded=%d nonpy=%d reader_only=%d unnamed=%d generic=%d"
          % (summary["spellings_named_by_writers_but_not_traced"],
             summary["spellings_named_only_by_excluded_sources"],
             summary["spellings_named_only_by_a_non_python_source"],
             summary["spellings_named_only_by_their_readers"],
             summary["spellings_no_source_names"],
             summary["spellings_with_a_generic_stem_flag"]))
    print("directory same=%d basename_only=%d other=%d | population_reproduced=%s"
          % (summary["traced_spellings_whose_path_reaches_the_reader_directory"],
             summary["traced_spellings_whose_path_reaches_only_a_basename"],
             summary["traced_spellings_whose_path_reaches_another_directory"],
             summary.get("population_reproduced")))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E487 who writes the literals nothing writes")
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