"""E439: price the directory-onto-a-file-slot class at the call slot, not at the temp rows.

E438 graded 203 temp-supplying call rows and found 56 that hand a directory to a callee whose only
write is the parameter path itself -- eleven ``json.dump``/``save``/``write_json``/``_write_csv``
wrappers.  That number answers "how many of the temp rows are misdirected".  It cannot answer "how
large is the misdirection", because the population was temp rows by construction: a wrapper that
takes a path is called from everywhere, and most calls hand it a file.

So this study keeps E438's class definition (imported, never re-implemented) and moves the unit from
the temp row to the call row: every corpus-wide call row that supplies an argument to one of those
eleven wrappers is graded by the shape of the argument it passes.

  * literal_file        -- 'results/x.json' (a lone quoted leaf): correct usage
  * composed_file       -- os.path.join(base, 'x.json') / f'{base}/x.json': correct usage
  * literal_directory   -- 'results/state_tilt' (a lone quoted path with no leaf)
  * dirname_expression  -- os.path.dirname(p) / Path(p).parent: a directory by construction
  * temp_derived        -- mkdtemp / TemporaryDirectory / tmpdir: a directory by construction
  * runtime             -- a short expression whose shape this scan cannot see
  * unmeasured          -- the argument text did not resolve to one expression at all

The three directory shapes are directories handed to a file slot; ``runtime`` and ``unmeasured``
are published as their own mass rather than folded into either side, because calling an unresolved
expression a file would manufacture the all-clear this study exists to test.

Two attribution gates sit between the corpus and the row count, and both exist because a first
draft of this study measured 24,918 rows whose arguments were mostly JSON payloads:

  * the argument must resolve to one short single-line expression.  The call index is keyed by
    callee name, so a row can be a call to a *different* function of the same arity; without this
    gate a `dump(payload, path)` row supplies a whole payload for the path position and it gets
    graded as a directory because the payload happens to contain "dirname".
  * the caller must be able to see the definition: the defining module itself, or a module that
    imports it.  A name-keyed index counts every `lst.append(x)` as a call to the wrapper named
    `append`; the reachability set removes them and the removed mass is published as
    ``rows_the_name_index_overstated`` rather than dropped.

The wrapper set is read from E438's face and re-confirmed against the live tree before its calls
are priced, so a wrapper that has moved refuses its own row count instead of being priced stale.

Usage:
    python scripts/e439_file_slot_callers.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import ast
import os
import re
import sys
from datetime import date

import e429_two_hop_writer as e420
import e432_fixture_write as e432
import e437_name_recall as e437
import e438_temp_write_base as e438

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST

CARD = os.path.join(ST, "tempwritebase_latest.json")
FACE_NAME = "fileslot_latest.json"

REACH_PROD = e432.REACH_PROD
REACH_TEST = e432.REACH_TEST

S_LITERAL_FILE = "the_argument_is_a_literal_file_path"
S_COMPOSED_FILE = "the_argument_composes_a_name_onto_a_base"
S_COMPOSED_DIR = "the_argument_composes_a_path_that_names_no_leaf"
S_LITERAL_DIR = "the_argument_is_a_literal_directory"
S_DIRNAME = "the_argument_is_a_dirname_expression"
S_TEMP = "the_argument_is_temp_derived"
S_RUNTIME = "the_argument_is_a_runtime_expression"
S_UNMEASURED = "the_argument_text_did_not_resolve_to_one_expression"

SHAPE_VOCAB = (S_LITERAL_FILE, S_COMPOSED_FILE, S_COMPOSED_DIR, S_LITERAL_DIR, S_DIRNAME, S_TEMP,
               S_RUNTIME, S_UNMEASURED)
FILE_SHAPES = (S_LITERAL_FILE, S_COMPOSED_FILE)
DIRECTORY_SHAPES = (S_COMPOSED_DIR, S_LITERAL_DIR, S_DIRNAME, S_TEMP)

V_NO_ROWS = "no_call_row_supplies_an_argument_to_a_file_path_wrapper"
V_NO_DIRECTORY = "no_call_row_hands_a_directory_to_a_file_path_wrapper"
V_SOME_DIR = "some_call_rows_hand_a_directory_to_a_file_path_wrapper"
VERDICT_VOCAB = (V_NO_ROWS, V_NO_DIRECTORY, V_SOME_DIR)

R_CONFIRMED = "confirmed_a_file_path_writer_in_the_live_tree"
R_NOT_A_FILE_WRITER = "the_live_site_no_longer_writes_only_the_parameter_path"
R_ABSENT = "the_published_callee_is_not_a_write_site_in_the_live_scan"

_DIRNAME_RE = re.compile(r"(?:os\.path\.dirname\s*\(|\.parent\b|\bparent\s*/\s*|"
                         r"\bdirname\s*\()")
_COMPOSE_RE = re.compile(r"(?:os\.path\.join\s*\(|\bformat\s*\(|f[\"']|"
                         r"\+\s*[\"']|/\s*[\"'])")
_LEAF_RE = re.compile(r"[^/\\.]+\.(?:json|csv|txt|md|jsonl|parquet|png|py|xml|html|npz|npy|log|"
                      r"yaml|yml|tsv|xlsx|pdf)$", re.I)


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _lone_literal(text: str) -> bool:
    """Is the whole supplied text one quoted string?  (E432's rule, kept identical.)"""
    return e432._is_literal(text)


def _names_a_leaf(tail: str) -> bool:
    """Does this path tail name a file rather than a directory?

    ``runnable_pool.json`` and ``.csv`` are leaves; ``results`` and ``per2`` are not.  The
    short-extension form matters because half the composed names in this corpus end in
    ``".csv" % (code,)`` or ``f"{code}.csv"``, whose visible tail is only the suffix.
    """
    t = (tail or "").strip().replace("\\", "/")
    if not t or t.endswith("/"):
        return False
    last = t.split("/")[-1]
    return bool(re.search(r"\.[A-Za-z0-9]{1,8}$", last))


def _tail_of(node) -> str | None:
    """The text of the last path component of a composed expression, when it is a constant."""
    if isinstance(node, ast.Call):
        name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
        if name in ("join", "Path", "str", "format") and node.args:
            return _tail_of(node.args[-1])
        return None
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mod):
            return _tail_of(node.left)
        if isinstance(node.op, (ast.Div, ast.Add)):
            return _tail_of(node.right)
        return None
    if isinstance(node, ast.JoinedStr):
        for part in reversed(node.values):
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                return part.value
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _composed_shape(text: str) -> str:
    """A join is a file if its last component names a leaf, a directory if it does not.

    The temp base is not the question: ``os.path.join(mkdtemp(), "out.json")`` is a file path
    that happens to live in a temp directory, and grading it as a directory because the base is
    a temp marker would manufacture seventeen defects out of correct code.
    """
    try:
        node = ast.parse(text, mode="eval").body
    except (SyntaxError, ValueError):
        return S_TEMP if e437.is_temp_text(text) else S_RUNTIME
    tail = _tail_of(node)
    if tail is None:
        return S_TEMP if e437.is_temp_text(text) else S_RUNTIME
    return S_COMPOSED_FILE if _names_a_leaf(tail) else S_COMPOSED_DIR


def argument_shape(text: str) -> str:
    """Grade the text a caller passes into a path parameter.

    Order matters.  A dirname call is a directory by construction; a lone literal is settled by
    whether its basename has a leaf; a composed expression is settled by its tail (see
    ``_composed_shape``), because a temp base says where the path lives, not what it names; a bare
    temp marker is a directory; anything else is a runtime expression this scan cannot shape.
    """
    text = (text or "").strip()
    if not text:
        return S_RUNTIME
    if not e437.is_directory_expression(text):
        # a payload, a whole call, or a multi-line body: this is not the argument this slot got
        return S_UNMEASURED
    if _DIRNAME_RE.search(text):
        return S_DIRNAME
    if _lone_literal(text):
        return S_LITERAL_FILE if _names_a_leaf(text[1:-1]) else S_LITERAL_DIR
    if _COMPOSE_RE.search(text):
        return _composed_shape(text)
    if e437.is_temp_text(text):
        return S_TEMP
    return S_RUNTIME


def verdict_for(rows: list[dict]) -> str:
    """Recomputed from the published rows, never carried."""
    if not rows:
        return V_NO_ROWS
    if any(r.get("argument_shape") in DIRECTORY_SHAPES for r in rows):
        return V_SOME_DIR
    return V_NO_DIRECTORY


def wrapper_rows(face: dict) -> list[tuple[str, str]]:
    """The (file, function) pairs E438 classed as file-path writers -- read, not guessed."""
    pairs: set[tuple[str, str]] = set()
    for row in (face.get("rows") or []):
        if row.get("write_class") == e438.C_FILE_WRITER:
            pairs.add((row.get("callee_file"), row.get("callee_function")))
    return sorted(pairs)


def grade_live_site(site) -> str:
    """Re-run E438's grading on a live site and return its write class."""
    params = site.parameter_directories()
    kinds = [e438.write_kind(text, params) for text, _node in site.paths]
    cls = e438.class_of(kinds)
    if cls == e438.C_NAMES_ONLY and params and all(
            (text or "").strip() in params
            for text, kind in zip([t for t, _ in site.paths], kinds) if kind == e438.W_NAMED):
        cls = e438.C_FILE_WRITER
    return cls


def recheck(face: dict, param: list) -> list[dict]:
    """Re-confirm each wrapper against the live scan before pricing its calls."""
    by_key = {}
    for site in param:
        by_key.setdefault((site.path, site.func), []).append(site)
    out: list[dict] = []
    for path, func in wrapper_rows(face):
        sites = by_key.get((path, func)) or []
        cls = grade_live_site(sites[0]) if sites else None
        status = (R_CONFIRMED if cls == e438.C_FILE_WRITER
                  else (R_ABSENT if not sites else R_NOT_A_FILE_WRITER))
        out.append({
            "callee_file": path,
            "callee_function": func,
            "live_write_class": cls,
            "live_sites": len(sites),
            "recheck": status,
        })
    return out


def definition_counts(names: list[str], sources: list[str]) -> dict[str, list[str]]:
    """Where each wrapper name is defined, so an ambiguous name's row count can be flagged."""
    pats = {n: re.compile(r"^[ \t]*(?:async[ \t]+)?def[ \t]+%s[ \t]*\(" % re.escape(n), re.M)
            for n in names}
    found: dict[str, list[str]] = {n: [] for n in names}
    for rel in sources:
        try:
            src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for name, pat in pats.items():
            if pat.search(src):
                found[name].append(rel)
    return found


def _module_stem(path: str) -> str:
    base = os.path.basename(path)
    return base[:-3] if base.endswith(".py") else base


def _importer_re(stem: str) -> re.Pattern:
    esc = re.escape(stem)
    return re.compile(
        r"(?:^[ \t]*from[ \t]+[\w\.]*{s}[ \t]+import\b"
        r"|^[ \t]*import[ \t]+(?:[\w\.]+[ \t]*,[ \t]*)*[\w\.]*{s}\b"
        r"|import_module\([ \t]*[\"'][\w\.]*{s}[\"'])".format(s=esc), re.M)


def reachable_callers(path: str, sources: list[str]) -> list[str]:
    """Files that can call this module's definition: the module itself plus its importers.

    The name-keyed call index cannot tell `lst.append(x)` from a call to a wrapper named
    ``append``.  Reachability is the cheapest honest filter: a call row to a callee the caller
    cannot see is not evidence about that callee.
    """
    stem = _module_stem(path)
    pat = _importer_re(stem)
    out = [path]
    for rel in sources:
        if rel == path:
            continue
        try:
            src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if stem not in src:
            continue
        if pat.search(src):
            out.append(rel)
    return out


def _tally(rows: list[dict], key: str, vocab) -> dict:
    out = {v: 0 for v in vocab}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def build(cutoff: str | None = None) -> dict:
    face438 = _load(CARD)
    cut = cutoff or face438["evidence_cutoff"]
    wrappers = wrapper_rows(face438)
    sources = [p for p in e437.corpus()
               if not os.path.basename(p).startswith(("e439", "_e439", "run_e439"))]
    sites, _parsed = e420.scan_corpus(sources)
    print(f"stage: {len(sources)} sources parsed", flush=True)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print(f"stage: {len(param)} parameter sites", flush=True)

    checks = recheck(face438, param)
    confirmed = {(c["callee_file"], c["callee_function"]) for c in checks
                 if c["recheck"] == R_CONFIRMED}
    print(f"stage: {len(confirmed)}/{len(wrappers)} wrappers confirmed live", flush=True)

    rows_all = e437.call_rows(param, index)
    print(f"stage: {len(rows_all)} directory-parameter call rows", flush=True)
    defs = definition_counts(sorted({f for _p, f in wrappers}), sources)
    reach = {(path, func): set(reachable_callers(path, sources)) for path, func in wrappers}
    print("stage: " + ", ".join("%s=%d" % (_module_stem(p), len(reach[(p, f)]))
                                for p, f in wrappers), flush=True)

    published: list[dict] = []
    overstated = 0
    by_name: dict[tuple, int] = {}
    for r in rows_all:
        key = (r["callee_file"], r["callee_function"])
        if key not in confirmed:
            continue
        by_name[key] = by_name.get(key, 0) + 1
        if r["caller_file"] not in reach[key]:
            overstated += 1
            continue
        shape = argument_shape(r["argument"])
        published.append({
            "wrapper_file": r["callee_file"],
            "wrapper_function": r["callee_function"],
            "caller_file": r["caller_file"],
            "caller_function": r["caller_function"],
            "caller_line": r["caller_line"],
            "argument": r["argument"][:200],
            "argument_shape": shape,
            "argument_is_a_directory": shape in DIRECTORY_SHAPES,
            "caller_kind": e437.caller_kind({"file": r["caller_file"],
                                             "caller": r["caller_function"]}),
            "name_definitions": len(defs.get(r["callee_function"]) or []),
        })
    published.sort(key=lambda x: (x["argument_shape"], x["wrapper_file"] or "",
                                  x["caller_line"] or 0))

    by_shape = _tally(published, "argument_shape", SHAPE_VOCAB)
    measured = [r for r in published if r["argument_shape"] != S_UNMEASURED]
    dir_rows = [r for r in published if r["argument_is_a_directory"]]

    # E438's own population, re-priced: how many of its 56 rows a caller can even see the
    # wrapper from.  A row that names a wrapper it cannot reach is a same-name call, and E438's
    # temp filter did not have a way to notice.
    card_rows = [r for r in (face438.get("rows") or [])
                 if r.get("write_class") == e438.C_FILE_WRITER]
    card_kept = [r for r in card_rows
                 if r["caller_file"] in reach.get(
                     (r["callee_file"], r["callee_function"]), set())]
    card_shapes = _tally([{"argument_shape": argument_shape(r.get("argument"))}
                          for r in card_kept], "argument_shape", SHAPE_VOCAB)
    card_block = {
        "rows_published_by_E438": len(card_rows),
        "rows_attributed_to_their_wrapper": len(card_kept),
        "rows_dropped_by_reachability": len(card_rows) - len(card_kept),
        "attributed_rows_handing_a_directory": sum(
            card_shapes.get(s, 0) for s in DIRECTORY_SHAPES),
        "attributed_rows_by_shape": card_shapes,
        "dropped_by_wrapper": _tally(
            [{"wrapper_function": r["callee_function"]} for r in card_rows
             if r not in card_kept], "wrapper_function", sorted(
                 {r["callee_function"] for r in card_rows})),
        "reading": "E438's 56 rows were counted by callee name; re-priced by whether the caller "
                   "can see the definition, the rows that survive all hand a temp directory to a "
                   "file-path wrapper -- the drop is same-name calls (write/save/dump/append on "
                   "something else), not a correction of E438's grading",
    }
    per_wrapper = []
    for path, func in wrappers:
        mine = [r for r in published if (r["wrapper_file"], r["wrapper_function"]) == (path, func)]
        per_wrapper.append({
            "callee_file": path,
            "callee_function": func,
            "caller_files_that_can_see_it": len(reach[(path, func)]),
            "rows_by_the_name_index": by_name.get((path, func), 0),
            "rows": len(mine),
            "rows_measured": sum(1 for r in mine if r["argument_shape"] != S_UNMEASURED),
            "rows_by_shape": _tally(mine, "argument_shape", SHAPE_VOCAB),
            "directory_rows": sum(1 for r in mine if r["argument_is_a_directory"]),
            "production_rows": sum(1 for r in mine if r["caller_kind"] == REACH_PROD),
            "test_rows": sum(1 for r in mine if r["caller_kind"] == REACH_TEST),
            "temp_rows": sum(1 for r in mine if r["argument_shape"] == S_TEMP),
            "name_definitions": len(defs.get(func) or []),
        })
    summary = {
        "corpus_sources": len(sources),
        "wrapers_priced": len(confirmed),
        "call_rows_into_the_wrappers": len(published),
        "rows_by_the_name_index": sum(by_name.values()),
        "rows_the_name_index_overstated": overstated,
        "rows_measured": len(measured),
        "rows_by_argument_shape": by_shape,
        "rows_handing_a_directory": len(dir_rows),
        "share_handing_a_directory": (round(len(dir_rows) / len(published), 4)
                                      if published else None),
        "share_of_measured_rows_handing_a_directory": (round(len(dir_rows) / len(measured), 4)
                                                       if measured else None),
        "e438_population_recheck": card_block,
        "directory_rows_by_shape": {s: by_shape.get(s, 0) for s in DIRECTORY_SHAPES},
        "directory_rows_by_caller_kind": _tally(dir_rows, "caller_kind",
                                                (REACH_PROD, REACH_TEST)),
        "temp_derived_directory_rows": by_shape.get(S_TEMP, 0),
        "unknown_rows": by_shape.get(S_RUNTIME, 0),
        "unmeasured_rows": by_shape.get(S_UNMEASURED, 0),
        "rows_under_an_ambiguous_wrapper_name": sum(
            1 for r in published if r["name_definitions"] > 1),
        "attribution": {
            "method": "caller file must be the defining module or a module that imports it",
            "rows_kept": len(published),
            "rows_dropped": overstated,
        },
        "wrapper_recheck": {
            "confirmed": sum(1 for c in checks if c["recheck"] == R_CONFIRMED),
            "not_a_file_writer": sum(1 for c in checks if c["recheck"] == R_NOT_A_FILE_WRITER),
            "absent_from_scan": sum(1 for c in checks if c["recheck"] == R_ABSENT),
            "rows": checks,
        },
        "per_wrapper": per_wrapper,
        "directory_row_examples": [
            {"wrapper": r["wrapper_function"], "caller_file": r["caller_file"],
             "caller_line": r["caller_line"], "argument": r["argument"],
             "shape": r["argument_shape"]}
            for r in dir_rows[:12]
        ],
    }
    return {
        "study": "E439_which_file_path_wrapper_is_called_with_a_directory_and_from_where",
        "card": "E439-WHICH-FILE-PATH-WRAPPER-IS-CALLED-WITH-A-DIRECTORY-AND-FROM-WHERE",
        "title": "price the directory-onto-a-file-slot class at the call slot by grading the "
                 "shape of every argument passed into E438's file-path wrappers",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(published),
        "shape_vocab": list(SHAPE_VOCAB),
        "directory_shapes": list(DIRECTORY_SHAPES),
        "file_shapes": list(FILE_SHAPES),
        "summary": summary,
        "rows": published,
        "method_limits": [
            "the wrapper set is E438's: the eleven (file, function) pairs it classed as file-path "
            "writers, re-confirmed against the live scan; a wrapper that has moved is reported in "
            "wrapper_recheck and its rows are excluded rather than priced from a stale row",
            "attribution is module reachability: the defining module plus modules that import it "
            "by name. A caller that reaches the wrapper through a dynamic import, a registry, or "
            "a re-export chain is dropped, so every per-wrapper row count is a floor and "
            "rows_the_name_index_overstated is the size of what the name index added",
            "argument shapes are read from the resolved text with no type inference: a bare name "
            "bound to a directory further up reads as runtime, so rows_handing_a_directory is a "
            "floor and unknown_rows plus unmeasured_rows is the mass that could still be a "
            "directory",
            "only call rows that reach a directory-named parameter enter the population; a call "
            "that passes a directory positionally into a parameter named p is outside this scan",
            "unmeasured is not a defect class: it is the share of attributed rows whose argument "
            "text did not resolve to one expression, so any ratio that leaves it out states which "
            "denominator it used",
        ],
    }


def write_face(face: dict) -> str:
    # The card's deliverable is a dated face; the family convention also keeps a *_latest mirror.
    # Writing only the mirror left results/state_tilt/FILESLOT-<cutoff>.json missing while the
    # card claimed it (r1458 fix), so both targets are written from one payload.
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    targets = [path,
               os.path.join(OUTDIR, "FILESLOT-%s.json" % face.get("evidence_cutoff"))]
    for target in targets:
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    if face.get("verdict") != verdict_for(rows):
        problems.append("verdict does not re-derive from the rows")
    tally = {v: 0 for v in SHAPE_VOCAB}
    for r in rows:
        shape = r.get("argument_shape")
        if shape not in SHAPE_VOCAB:
            problems.append("%s:%s shape outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
            continue
        tally[shape] += 1
        want_dir = shape in DIRECTORY_SHAPES
        if bool(r.get("argument_is_a_directory")) != want_dir:
            problems.append("%s:%s directory flag disagrees with its shape"
                            % (r.get("caller_file"), r.get("caller_line")))
        if not (r.get("argument") or "").strip():
            problems.append("%s:%s carries an empty argument"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("caller_kind") not in (REACH_PROD, REACH_TEST):
            problems.append("%s:%s caller kind outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
    if tally != (s.get("rows_by_argument_shape") or {}):
        problems.append("rows_by_argument_shape does not re-derive from the rows")
    if sum(tally.values()) != s.get("call_rows_into_the_wrappers"):
        problems.append("the shape tally does not close against the row list")
    measured = sum(1 for r in rows if r.get("argument_shape") != S_UNMEASURED)
    if measured != s.get("rows_measured"):
        problems.append("rows_measured does not re-derive")
    if s.get("rows_measured") != s["call_rows_into_the_wrappers"] - s.get("unmeasured_rows", 0):
        problems.append("rows_measured does not equal the rows minus the unmeasured ones")
    attr = s.get("attribution") or {}
    if attr.get("rows_kept") != len(rows):
        problems.append("attribution rows_kept does not match the published rows")
    if attr.get("rows_dropped", 0) + attr.get("rows_kept", 0) != s.get("rows_by_the_name_index"):
        problems.append("the name-index total does not close over kept plus dropped rows")
    if attr.get("rows_dropped") != s.get("rows_the_name_index_overstated"):
        problems.append("rows_the_name_index_overstated does not re-derive")
    dirs = sum(1 for r in rows if r.get("argument_is_a_directory"))
    if dirs != s.get("rows_handing_a_directory"):
        problems.append("rows_handing_a_directory does not re-derive")
    want = {sh: tally.get(sh, 0) for sh in DIRECTORY_SHAPES}
    if want != (s.get("directory_rows_by_shape") or {}):
        problems.append("directory_rows_by_shape does not re-derive")
    if sum(want.values()) != dirs:
        problems.append("the directory shape breakdown does not add up")
    by_kind = _tally([r for r in rows if r.get("argument_is_a_directory")], "caller_kind",
                     (REACH_PROD, REACH_TEST))
    if by_kind != (s.get("directory_rows_by_caller_kind") or {}):
        problems.append("directory_rows_by_caller_kind does not re-derive")
    if s.get("call_rows_into_the_wrappers") and s.get("share_handing_a_directory") is not None:
        share = round(dirs / s["call_rows_into_the_wrappers"], 4)
        if abs(share - s["share_handing_a_directory"]) > 1e-9:
            problems.append("the published share does not re-derive")
    reason = s.get("wrapper_recheck") or {}
    if (reason.get("confirmed", 0) + reason.get("not_a_file_writer", 0)
            + reason.get("absent_from_scan", 0)) != len(reason.get("rows") or []):
        problems.append("wrapper_recheck does not close against its row list")
    if reason.get("confirmed") != s.get("wrapers_priced"):
        problems.append("wrapers_priced does not re-derive from the recheck")
    per = s.get("per_wrapper") or []
    if len(per) != len(reason.get("rows") or []):
        problems.append("per_wrapper does not cover every wrapper in the recheck")
    for block in per:
        mine = [r for r in rows
                if (r.get("wrapper_file"), r.get("wrapper_function"))
                == (block.get("callee_file"), block.get("callee_function"))]
        if block.get("rows") != len(mine):
            problems.append("%s: per_wrapper row count does not re-derive"
                            % block.get("callee_function"))
        if block.get("rows_by_the_name_index", 0) < block.get("rows", 0):
            problems.append("%s: per_wrapper name-index count is below its attributed rows"
                            % block.get("callee_function"))
        if block.get("rows_measured") != sum(1 for r in mine
                                             if r.get("argument_shape") != S_UNMEASURED):
            problems.append("%s: per_wrapper measured count does not re-derive"
                            % block.get("callee_function"))
        if block.get("directory_rows") != sum(1 for r in mine
                                              if r.get("argument_is_a_directory")):
            problems.append("%s: per_wrapper directory count does not re-derive"
                            % block.get("callee_function"))
        if block.get("production_rows", 0) + block.get("test_rows", 0) != block.get("rows"):
            problems.append("%s: per_wrapper caller split does not close"
                            % block.get("callee_function"))
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    if live["summary"]["rows_by_argument_shape"] != face["summary"]["rows_by_argument_shape"]:
        problems.append("live shape tally differs from the published face")
    if live["summary"]["call_rows_into_the_wrappers"] \
            != face["summary"]["call_rows_into_the_wrappers"]:
        problems.append("live call-row count differs from the published face")
    if live["summary"]["wrapers_priced"] != face["summary"]["wrapers_priced"]:
        problems.append("the live wrapper recheck differs from the published face")
    if live["summary"]["rows_the_name_index_overstated"] \
            != face["summary"]["rows_the_name_index_overstated"]:
        problems.append("the live attribution drop differs from the published face")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    check("shape_literal_file", argument_shape("'results/x.json'") == S_LITERAL_FILE)
    check("shape_literal_nested_file",
          argument_shape("'results/state_tilt/x.parquet'") == S_LITERAL_FILE)
    check("shape_literal_dir", argument_shape("'results/state_tilt'") == S_LITERAL_DIR)
    check("shape_literal_dir_slash", argument_shape("'results/state_tilt/'") == S_LITERAL_DIR)
    check("shape_dirname", argument_shape("os.path.dirname(p)") == S_DIRNAME)
    check("shape_parent", argument_shape("Path(p).parent") == S_DIRNAME)
    check("shape_temp", argument_shape("tempfile.mkdtemp()") == S_TEMP)
    check("shape_tempdir_var", argument_shape("tmpdir") == S_TEMP)
    check("shape_composed_join",
          argument_shape("os.path.join(base, 'x.json')") == S_COMPOSED_FILE)
    check("shape_composed_fstring", argument_shape("f'{base}/x.json'") == S_COMPOSED_FILE)
    check("shape_temp_base_with_a_leaf",
          argument_shape("os.path.join(tempfile.mkdtemp(prefix=\"p_\"), \"results\", "
                         "\"runnable_pool.json\")") == S_COMPOSED_FILE)
    check("shape_temp_base_with_a_formatted_leaf",
          argument_shape("os.path.join(os.path.join(tempfile.mkdtemp(prefix=\"e_\"), "
                         "\"panel\"), \"sh%06d.csv\" % (510000 + s))") == S_COMPOSED_FILE)
    check("shape_temp_base_with_an_fstring_leaf",
          argument_shape("os.path.join(tempfile.mkdtemp(prefix=\"leg3_\"), f\"{code}.csv\")")
          == S_COMPOSED_FILE)
    check("shape_composed_without_a_leaf",
          argument_shape("os.path.join(tempfile.mkdtemp(prefix=\"p_\"), \"results\")")
          == S_COMPOSED_DIR)
    check("shape_bare_temp_marker",
          argument_shape("tempfile.mkdtemp(prefix=\"p_\")") == S_TEMP)
    check("leaf_test_short_extension", _names_a_leaf(".csv") and not _names_a_leaf("per2"))
    check("leaf_test_rejects_a_trailing_slash", not _names_a_leaf("results/"))
    check("shape_runtime", argument_shape("out") == S_RUNTIME)
    check("shape_empty", argument_shape("") == S_RUNTIME)
    check("shape_unmeasured_payload",
          argument_shape("{\n \"batch\": 1,\n \"generated\": x\n}") == S_UNMEASURED)
    check("shape_long_text_is_unmeasured",
          argument_shape("a" * 300) == S_UNMEASURED)
    check("literal_rule_reused", _lone_literal("'a/b.json'") and not _lone_literal("a['k']"))
    check("importer_re_matches_plain_import",
          bool(_importer_re("e439_x").search("import e439_x\n")))
    check("importer_re_matches_from_import",
          bool(_importer_re("e439_x").search("from scripts.e439_x import run\n")))
    check("importer_re_matches_import_module",
          bool(_importer_re("e439_x").search("m = import_module('e439_x')\n")))
    check("importer_re_rejects_a_plain_mention",
          not _importer_re("e439_x").search("# e439_x is mentioned here\n"))
    check("module_stem_strips_py", _module_stem("scripts/e439_x.py") == "e439_x")

    f_row = {"argument_shape": S_LITERAL_FILE, "argument_is_a_directory": False,
             "caller_file": "scripts/x.py", "caller_line": 1, "argument": "'a.json'",
             "caller_kind": REACH_PROD, "wrapper_file": "scripts/w.py",
             "wrapper_function": "save", "name_definitions": 1}
    c_row = dict(f_row, argument_shape=S_COMPOSED_FILE, argument="os.path.join(b, 'a.json')",
                 caller_line=2)
    d_row = dict(f_row, argument_shape=S_LITERAL_DIR, argument_is_a_directory=True,
                 argument="'results/state_tilt'", caller_line=3)
    u_row = dict(f_row, argument_shape=S_RUNTIME, argument="out", caller_line=4)
    check("verdict_no_directory", verdict_for([f_row, c_row]) == V_NO_DIRECTORY)
    check("verdict_some_dir", verdict_for([f_row, d_row]) == V_SOME_DIR)
    check("verdict_unknown_is_not_a_file", verdict_for([u_row]) == V_NO_DIRECTORY)
    check("verdict_unmeasured_is_not_a_directory",
          verdict_for([dict(u_row, argument_shape=S_UNMEASURED)]
                      ) == V_NO_DIRECTORY)
    check("verdict_empty", verdict_for([]) == V_NO_ROWS)

    def face_of(rows: list[dict]) -> dict:
        dirs = [r for r in rows if r["argument_is_a_directory"]]
        measured = [r for r in rows if r["argument_shape"] != S_UNMEASURED]
        return {
            "verdict": verdict_for(rows),
            "rows": rows,
            "summary": {
                "rows_by_argument_shape": _tally(rows, "argument_shape", SHAPE_VOCAB),
                "call_rows_into_the_wrappers": len(rows),
                "rows_by_the_name_index": len(rows),
                "rows_the_name_index_overstated": 0,
                "rows_measured": len(measured),
                "unmeasured_rows": len(rows) - len(measured),
                "rows_handing_a_directory": len(dirs),
                "directory_rows_by_shape": {s: sum(1 for r in rows
                                                   if r["argument_shape"] == s)
                                            for s in DIRECTORY_SHAPES},
                "directory_rows_by_caller_kind": _tally(dirs, "caller_kind",
                                                        (REACH_PROD, REACH_TEST)),
                "share_handing_a_directory": (round(len(dirs) / len(rows), 4)
                                              if rows else None),
                "attribution": {"method": "fixture", "rows_kept": len(rows),
                                "rows_dropped": 0},
                "wrapers_priced": 1,
                "wrapper_recheck": {"confirmed": 1, "not_a_file_writer": 0,
                                    "absent_from_scan": 0,
                                    "rows": [{"callee_file": "scripts/w.py",
                                              "callee_function": "save",
                                              "recheck": R_CONFIRMED}]},
                "per_wrapper": [{"callee_file": "scripts/w.py", "callee_function": "save",
                                 "caller_files_that_can_see_it": 1,
                                 "rows_by_the_name_index": len(rows),
                                 "rows": len(rows),
                                 "rows_measured": len(measured),
                                 "rows_by_shape": _tally(rows, "argument_shape", SHAPE_VOCAB),
                                 "directory_rows": len(dirs),
                                 "production_rows": sum(1 for r in rows
                                                        if r["caller_kind"] == REACH_PROD),
                                 "test_rows": sum(1 for r in rows
                                                  if r["caller_kind"] == REACH_TEST),
                                 "temp_rows": sum(1 for r in rows
                                                  if r["argument_shape"] == S_TEMP),
                                 "name_definitions": 1}],
            },
        }

    good = face_of([f_row, d_row, u_row])
    check("tally_clean", tally_problems(good) == [])
    bad = json.loads(json.dumps(good))
    bad["summary"]["rows_by_argument_shape"][S_LITERAL_FILE] = 5
    check("tally_catches_a_shifted_cell", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(good))
    bad2["rows"][1]["argument_is_a_directory"] = False
    check("tally_catches_a_wrong_directory_flag", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(good))
    bad3["verdict"] = V_NO_DIRECTORY
    check("tally_catches_a_carried_verdict", tally_problems(bad3) != [])
    bad4 = json.loads(json.dumps(good))
    bad4["summary"]["per_wrapper"][0]["directory_rows"] = 0
    check("tally_catches_a_wrapper_block", tally_problems(bad4) != [])
    bad5 = json.loads(json.dumps(good))
    bad5["summary"]["wrapers_priced"] = 2
    check("tally_catches_a_wrapper_count", tally_problems(bad5) != [])
    bad6 = json.loads(json.dumps(good))
    bad6["summary"]["rows_the_name_index_overstated"] = 1
    check("tally_catches_a_broken_attribution_close", tally_problems(bad6) != [])
    bad7 = json.loads(json.dumps(good))
    bad7["summary"]["rows_measured"] = 99
    check("tally_catches_a_measured_count", tally_problems(bad7) != [])

    for name in fails:
        print("FAIL", name)
    print(f"selftest {legs - len(fails)}/{legs}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        path = write_face(face)
        problems = tally_problems(face)
        print(f"verdict: {face['verdict']}")
        print(json.dumps(face["summary"]["rows_by_argument_shape"], ensure_ascii=False))
        print(f"rows handing a directory: {face['summary']['rows_handing_a_directory']} of "
              f"{face['summary']['call_rows_into_the_wrappers']}")
        print(f"face: {_rel(path)}")
        if problems:
            for p in problems:
                print("PROBLEM", p)
            return 1
        return 0
    if cmd == "verify":
        problems = verify()
        print("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 1 if problems else 0
    print("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))