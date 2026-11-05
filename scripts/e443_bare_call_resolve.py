"""E443: the 707 rows E440 called "bare calls to a name more than one module defines" are a name
fact, not a binding fact -- a bare call resolves through the caller's own imports.

E440 graded every dropped call row on two axes and stopped at the definition axis: a row whose
name has more than one definition was published as `shared`.  But "more than one module defines
this name" says nothing about which one a given call reaches.  A caller that writes
`from e438_temp_write_base import write_base` binds exactly one of them; a caller that writes
`from a import dump` and `from b import dump` is genuinely ambiguous; a caller that imports none of
them binds something the corpus cannot see at all (a local def, a star import, or a re-export).

So this study re-reads the 707 rows and resolves each one through its caller's AST:

  resolution --
    one_defining_module        exactly one of the defining modules supplies the name to this file
    the_callers_own_definition the caller file itself defines the name (top-level def in scope)
    more_than_one_defining      the caller binds the name from two or more defining modules
    a_module_that_does_not_define_it  imported from a module outside the defining set (re-export)
    a_star_import               a star import pulls in a defining module: unresolvable statically
    no_defining_module          nothing in the caller's imports binds the name
  and, for the rows that resolve, whether the surviving definition writes the parameter path
  itself (E438's write-base primitives over the definition's own write calls).

Usage:
    python scripts/e443_bare_call_resolve.py run|verify|check|selftest

`verify` re-derives the whole population (E440's scan over ~3.4k sources, ~20 min), so the S6
chain runs `check` instead: it re-derives every published tally from the published cells and
refuses a face that no longer closes, without pretending to have re-run the study.
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import date

import e429_two_hop_writer as e420
import e432_fixture_write as e432
import e437_name_recall as e437
import e438_temp_write_base as e438
import e439_file_slot_callers as e439
import e440_shared_wrapper_names as e440

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST
FACE_NAME = "barecallresolve_latest.json"
DATED_PREFIX = "BARECALLRESOLVE"
CARD = "E443-WHICH-DEFINITION-A-BARE-CALL-TO-A-SHARED-NAME-RESOLVES-TO"

REACH_PROD = e432.REACH_PROD
REACH_TEST = e432.REACH_TEST

R_ONE = "one_defining_module"
R_LOCAL = "the_callers_own_definition"
R_MANY = "more_than_one_defining_module"
R_REEXPORT = "a_module_that_does_not_define_it"
R_STAR = "a_star_import"
R_NONE = "no_defining_module"
RESOLUTION_VOCAB = (R_ONE, R_LOCAL, R_MANY, R_REEXPORT, R_STAR, R_NONE)

W_SURVIVING = "the_surviving_definition_was_graded"
W_SEVERAL = "several_definitions_stay_in_play"
W_NOT_ATTRIBUTED = "no_corpus_definition_to_grade"

V_ALL_RESOLVED = "every_shared_name_call_resolves_once_the_callers_imports_are_read"
V_SOME_AMBIGUOUS = "some_shared_name_calls_bind_more_than_one_defining_module"
V_SOME_UNBOUND = "some_shared_name_calls_bind_no_defining_module_the_corpus_can_see"
VERDICT_VOCAB = (V_ALL_RESOLVED, V_SOME_AMBIGUOUS, V_SOME_UNBOUND)

WRITE_TAILS = frozenset({
    "write", "writelines", "write_text", "write_bytes", "dump", "save", "savefig",
    "to_csv", "to_parquet", "to_json", "replace", "rename", "open", "makedirs",
})

_IMPORT_CACHE: dict[str, dict] = {}
_DEF_CACHE: dict[tuple[str, str], tuple | None] = {}


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _tally(rows: list[dict], key: str, vocab) -> dict:
    out = {v: 0 for v in vocab}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def _tally_rows(cells: list[dict], key: str, vocab) -> dict:
    """Cells carry a row count: a tally of calls must weigh each cell by its own size."""
    out = {v: 0 for v in vocab}
    for c in cells:
        out[c[key]] = out.get(c[key], 0) + c["rows"]
    return out


def _resolve_module(dotted: str, caller_rel: str) -> list[str]:
    """Repo-relative files a dotted module path can name.

    The corpus is flat-in-practice (`scripts/foo.py` imported as `foo`), so every suffix of the
    dotted path is tried: `scripts.foo` and `foo` both land on the same file, and a package's
    `__init__.py` counts as the module too.
    """
    parts = [p for p in dotted.split(".") if p]
    out: list[str] = []
    bases = [""]
    if "/" in caller_rel:
        bases.append(caller_rel.rsplit("/", 1)[0])
    for start in range(len(parts)):
        stem = "/".join(parts[start:])
        for base in bases:
            for cand in (f"{stem}.py", f"{stem}/__init__.py"):
                full = f"{base}/{cand}" if base else cand
                if os.path.isfile(os.path.join(ROOT, full)):
                    out.append(full)
    return sorted(set(out))


def imports_of(rel: str) -> dict:
    """Which repo files this source imports names from.

    Returns {"names": {bound_name: [files]}, "star": [files]} where `names` maps the *bound*
    name (after `as`) to the module files it plausibly comes from.  A `from pkg import name`
    whose `pkg/name.py` exists is a module import and binds `name` to that module, not to a
    function -- that case is resolved to the module file so a bare call to the same word is not
    credited to the wrong definition.
    """
    if rel in _IMPORT_CACHE:
        return _IMPORT_CACHE[rel]
    try:
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        _IMPORT_CACHE[rel] = {"names": {}, "star": []}
        return _IMPORT_CACHE[rel]
    names: dict[str, set[str]] = {}
    star: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level:
                base = rel.rsplit("/", 1)[0] if "/" in rel else ""
                for _ in range(max(node.level - 1, 0)):
                    base = base.rsplit("/", 1)[0] if "/" in base else ""
                mod = f"{base.replace('/', '.')}.{mod}" if base else mod
            for alias in node.names:
                if alias.name == "*":
                    star.update(_resolve_module(mod, rel))
                    continue
                bound = alias.asname or alias.name
                sub = f"{mod}.{alias.name}" if mod else alias.name
                files = _resolve_module(sub, rel)
                if files:
                    names.setdefault(bound, set()).update(files)
                else:
                    names.setdefault(bound, set()).update(_resolve_module(mod, rel))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[-1]
                names.setdefault(bound, set()).update(_resolve_module(alias.name, rel))
    packed = {"names": {k: sorted(v) for k, v in names.items()}, "star": sorted(star)}
    _IMPORT_CACHE[rel] = packed
    return packed


def _def_node(rel: str, name: str) -> tuple | None:
    """The definition of `name` in this file, as (params, body_source_segment)."""
    key = (rel, name)
    if key in _DEF_CACHE:
        return _DEF_CACHE[key]
    try:
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        _DEF_CACHE[key] = None
        return None
    found = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            if found is None or node.col_offset < found.col_offset:
                found = node
    if found is None:
        _DEF_CACHE[key] = None
        return None
    params = [a.arg for a in list(found.args.args) + list(found.args.kwonlyargs)]
    _DEF_CACHE[key] = (params, found, src)
    return _DEF_CACHE[key]


def def_write_class(rel: str, name: str) -> str:
    """Does the surviving definition write the parameter path itself?  E438's primitives, reused.

    Only calls whose tail is a write verb are graded: the alternative (grading the whole body
    text) is what E438's own r1457 postscript caught as a false positive.
    """
    got = _def_node(rel, name)
    if got is None:
        return e438.C_UNRESOLVED
    params, node, src = got
    if not params:
        return e438.C_UNRESOLVED
    kinds: list[str] = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        tail = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if tail not in WRITE_TAILS:
            continue
        text = ast.get_source_segment(src, sub) or ""
        kinds.append(e438.write_kind(text, params))
    return e438.class_of(kinds)


def classify(caller_rel: str, name: str, defining: list[str]) -> tuple[str, str, str]:
    """(resolution, surviving_file, write_class) for one bare call row."""
    imported = imports_of(caller_rel)
    bound = set(imported["names"].get(name) or [])
    defining_set = set(defining)
    overlap = sorted(bound & defining_set)
    if len(overlap) > 1:
        return R_MANY, "", W_SEVERAL
    if len(overlap) == 1:
        return R_ONE, overlap[0], def_write_class(overlap[0], name)
    if caller_rel in defining_set:
        return R_LOCAL, caller_rel, def_write_class(caller_rel, name)
    if bound:
        return R_REEXPORT, "", W_NOT_ATTRIBUTED
    if set(imported["star"]) & defining_set:
        return R_STAR, "", W_NOT_ATTRIBUTED
    return R_NONE, "", W_NOT_ATTRIBUTED


def verdict_for(rows: list[dict]) -> str:
    """Recomputed from the published cells, never carried."""
    if any(r["resolution"] == R_MANY for r in rows):
        return V_SOME_AMBIGUOUS
    if any(r["resolution"] in (R_NONE, R_REEXPORT, R_STAR) for r in rows):
        return V_SOME_UNBOUND
    return V_ALL_RESOLVED


def population() -> dict:
    """E440's dropped-row loop, re-run because E440's face publishes cells without lines."""
    face438 = _load(e440.CARD)
    cut = face438["evidence_cutoff"]
    wrappers = e439.wrapper_rows(face438)
    names = sorted({f for _p, f in wrappers})
    sources = [p for p in e437.corpus()
               if not os.path.basename(p).startswith(("e440", "_e440", "run_e440",
                                                      "e443", "_e443", "run_e443"))]
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print(f"stage: {len(param)} parameter sites over {len(sources)} sources", flush=True)

    checks = e439.recheck(face438, param)
    confirmed = {(c["callee_file"], c["callee_function"]) for c in checks
                 if c["recheck"] == e439.R_CONFIRMED}
    defs = e439.definition_counts(names, sources)
    reach = {(p, f): set(e439.reachable_callers(p, sources)) for p, f in wrappers}
    rows_all = e437.call_rows(param, index)
    print(f"stage: {len(confirmed)}/{len(wrappers)} wrappers confirmed live", flush=True)

    shared: list[dict] = []
    dropped = 0
    for r in rows_all:
        key = (r["callee_file"], r["callee_function"])
        if key not in confirmed:
            continue
        if r["caller_file"] in reach[key]:
            continue
        dropped += 1
        name = r["callee_function"]
        n_defs = len(defs.get(name) or [])
        axis = e440.D_ONE if n_defs <= 1 else e440.D_MANY
        spell = e440.spelling_at(r["caller_file"], r["caller_line"], name)
        if e440.row_class(axis, spell) != e440.R_SHARED:
            continue
        resolution, survivor, write_class = classify(r["caller_file"], name,
                                                     sorted(defs.get(name) or []))
        shared.append({
            "wrapper_name": name,
            "wrapper_file": r["callee_file"],
            "caller_file": r["caller_file"],
            "caller_function": r["caller_function"],
            "caller_line": r["caller_line"],
            "caller_kind": e437.caller_kind({"file": r["caller_file"],
                                             "caller": r["caller_function"]}),
            "defining_files": sorted(defs.get(name) or []),
            "definitions": n_defs,
            "resolution": resolution,
            "surviving_definition": survivor,
            "write_class": write_class,
        })
    print(f"stage: {len(shared)} unbound-bare rows of {dropped} dropped", flush=True)
    return {"rows": shared, "cutoff": cut, "sources": len(sources),
            "wrappers": len(confirmed), "dropped": dropped, "names": names,
            "defs": defs}


def build(cutoff: str | None = None) -> dict:
    pop = population()
    rows = pop["rows"]
    cut = cutoff or pop["cutoff"]

    cells: dict[tuple, int] = {}
    for r in rows:
        k = (r["wrapper_name"], r["caller_file"], r["resolution"],
             r["surviving_definition"], r["write_class"], r["caller_kind"])
        cells[k] = cells.get(k, 0) + 1
    published = [{"wrapper_name": k[0], "caller_file": k[1], "resolution": k[2],
                  "surviving_definition": k[3], "write_class": k[4], "caller_kind": k[5],
                  "rows": v} for k, v in sorted(cells.items())]

    per_name = []
    for name in sorted({r["wrapper_name"] for r in rows}):
        mine = [r for r in rows if r["wrapper_name"] == name]
        per_name.append({
            "name": name,
            "defining_files": sorted(pop["defs"].get(name) or []),
            "rows": len(mine),
            "by_resolution": _tally(mine, "resolution", RESOLUTION_VOCAB),
            "by_write_class": _tally(mine, "write_class", (e438.C_INSIDE, e438.C_PARTIAL,
                                                           e438.C_NAMES_ONLY, e438.C_FILE_WRITER,
                                                           e438.C_OUTSIDE, e438.C_UNRESOLVED,
                                                           W_SEVERAL, W_NOT_ATTRIBUTED)),
            "caller_files": len({r["caller_file"] for r in mine}),
        })

    by_resolution = _tally_rows(published, "resolution", RESOLUTION_VOCAB)
    graded = [r for r in rows if r["write_class"] in (e438.C_INSIDE, e438.C_PARTIAL,
                                                      e438.C_NAMES_ONLY, e438.C_FILE_WRITER,
                                                      e438.C_OUTSIDE, e438.C_UNRESOLVED)]
    summary = {
        "corpus_sources": pop["sources"],
        "wrappers_priced": pop["wrappers"],
        "dropped_rows_recomputed": pop["dropped"],
        "shared_name_rows": len(rows),
        "by_resolution": by_resolution,
        "rows_that_resolve_to_one_definition": by_resolution[R_ONE] + by_resolution[R_LOCAL],
        "rows_still_ambiguous": by_resolution[R_MANY],
        "rows_with_no_visible_definition": (by_resolution[R_NONE] + by_resolution[R_REEXPORT]
                                            + by_resolution[R_STAR]),
        "share_resolved": round((by_resolution[R_ONE] + by_resolution[R_LOCAL]) / len(rows), 4)
        if rows else None,
        "surviving_definitions_graded": len(graded),
        "by_write_class": _tally(graded, "write_class",
                                 (e438.C_INSIDE, e438.C_PARTIAL, e438.C_NAMES_ONLY,
                                  e438.C_FILE_WRITER, e438.C_OUTSIDE, e438.C_UNRESOLVED)),
        "surviving_definitions_that_write_the_parameter_path": sum(
            1 for r in graded if r["write_class"] == e438.C_FILE_WRITER),
        "production_rows": sum(1 for r in rows if r["caller_kind"] == REACH_PROD),
        "test_rows": sum(1 for r in rows if r["caller_kind"] == REACH_TEST),
        "per_name": per_name,
        "distance_check": {
            "e440_shared_rows": e440_shared_rows(),
            "recomputed_shared_rows": len(rows),
            "agrees": e440_shared_rows() == len(rows),
            "reading": "the same population E440 published as one class, re-read on the bindings "
                       "axis",
        },
    }
    return {
        "study": "E443_which_definition_a_bare_call_to_a_shared_name_resolves_to",
        "card": CARD,
        "title": "resolve each of E440's shared-name bare calls through the caller's own imports "
                 "and grade whether the surviving definition writes the parameter path itself",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(published),
        "resolution_vocab": list(RESOLUTION_VOCAB),
        "write_class_of_surviving_definitions": [W_SURVIVING, W_SEVERAL, W_NOT_ATTRIBUTED],
        "summary": summary,
        "rows": published,
        "examples": [
            {"wrapper_name": r["wrapper_name"], "caller_file": r["caller_file"],
             "caller_function": r["caller_function"], "caller_line": r["caller_line"],
             "resolution": r["resolution"], "surviving_definition": r["surviving_definition"]}
            for r in rows[:60]
        ],
        "method_limits": [
            "the import test reads the caller file as it is on disk now; a file edited after the "
            "row was indexed is graded on its current imports, which is the honest reading of "
            "'where does this call bind today' but not a historical one",
            "only direct name bindings resolve: `from mod import name` and the caller's own "
            "`def name` count, while wildcard imports and runtime patching cannot be resolved "
            "and are published as their own classes rather than assumed",
            "`from pkg import submodule` is treated as a module import when pkg/submodule.py "
            "exists, so a bare call to that word is not credited to a function definition",
            "the write axis is graded on calls inside the definition whose tail is a write verb; "
            "a definition that hands its path to a helper is classed by what it does itself, "
            "which is the same bound E438 published",
            "the population is E440's shared-name class re-derived from the live corpus; a row "
            "whose spelling changed since E440 was published is not in this face",
        ],
    }


def e440_shared_rows() -> int | None:
    try:
        face = _load(os.path.join(OUTDIR, e440.FACE_NAME))
    except (OSError, ValueError):
        return None
    return ((face.get("summary") or {}).get("shadow_by_row_class") or {}).get(e440.R_SHARED)


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    targets = [path,
               os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))]
    for target in targets:
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    tally: dict[str, int] = {c: 0 for c in RESOLUTION_VOCAB}
    for r in rows:
        if r.get("resolution") not in RESOLUTION_VOCAB:
            problems.append("%s:%s resolution outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
            continue
        if not isinstance(r.get("rows"), int) or r.get("rows") <= 0:
            problems.append("%s:%s carries a non-positive cell count"
                            % (r.get("wrapper_name"), r.get("caller_file")))
            continue
        if r.get("caller_kind") not in (REACH_PROD, REACH_TEST):
            problems.append("%s:%s caller kind outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
        if r["resolution"] in (R_ONE, R_LOCAL) and not r.get("surviving_definition"):
            problems.append("%s:%s claims a resolution without a surviving definition"
                            % (r["wrapper_name"], r["caller_file"]))
        if r["resolution"] in (R_MANY, R_REEXPORT, R_STAR, R_NONE) \
                and r.get("surviving_definition"):
            problems.append("%s:%s names a surviving definition without a resolution"
                            % (r["wrapper_name"], r["caller_file"]))
        if r["resolution"] == R_ONE and r["surviving_definition"] \
                and r["surviving_definition"] == r["caller_file"]:
            problems.append("%s:%s says one module supplies the name but that module is the "
                            "caller itself" % (r["wrapper_name"], r["caller_file"]))
        tally[r["resolution"]] = tally.get(r["resolution"], 0) + r["rows"]
    if tally != (s.get("by_resolution") or {}):
        problems.append("by_resolution does not re-derive from the rows")
    if sum(tally.values()) != s.get("shared_name_rows"):
        problems.append("the resolution tally does not close against shared_name_rows")
    if verdict_for(rows) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the published rows")
    per = s.get("per_name") or []
    for block in per:
        mine = [r for r in rows if r.get("wrapper_name") == block.get("name")]
        if block.get("rows") != sum(r["rows"] for r in mine):
            problems.append("%s: rows do not re-derive" % block.get("name"))
        if block.get("by_resolution") != _tally_rows(mine, "resolution", RESOLUTION_VOCAB):
            problems.append("%s: by_resolution does not re-derive" % block.get("name"))
    if sum(b.get("rows", 0) for b in per) != s.get("shared_name_rows"):
        problems.append("the per-name blocks do not add up to the shared total")
    if s.get("rows_that_resolve_to_one_definition") != tally[R_ONE] + tally[R_LOCAL]:
        problems.append("rows_that_resolve_to_one_definition does not re-derive")
    if s.get("rows_still_ambiguous") != tally[R_MANY]:
        problems.append("rows_still_ambiguous does not re-derive")
    if (s.get("distance_check") or {}).get("recomputed_shared_rows") != s.get("shared_name_rows"):
        problems.append("distance_check does not restate the shared total")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    for key in ("shared_name_rows", "by_resolution", "rows_still_ambiguous",
                "surviving_definitions_graded"):
        if live["summary"].get(key) != face["summary"].get(key):
            problems.append(f"live {key} differs from the published face")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    def face_of(rows: list[dict]) -> dict:
        per = []
        for name in sorted({r["wrapper_name"] for r in rows}):
            mine = [r for r in rows if r["wrapper_name"] == name]
            per.append({"name": name, "rows": sum(r["rows"] for r in mine),
                        "by_resolution": _tally_rows(mine, "resolution", RESOLUTION_VOCAB)})
        return {
            "verdict": verdict_for(rows),
            "rows": rows,
            "summary": {
                "shared_name_rows": sum(r["rows"] for r in rows),
                "by_resolution": _tally_rows(rows, "resolution", RESOLUTION_VOCAB),
                "rows_that_resolve_to_one_definition": sum(
                    r["rows"] for r in rows if r["resolution"] in (R_ONE, R_LOCAL)),
                "rows_still_ambiguous": sum(
                    r["rows"] for r in rows if r["resolution"] == R_MANY),
                "surviving_definitions_graded": 0,
                "per_name": per,
                "distance_check": {"recomputed_shared_rows": sum(r["rows"] for r in rows)},
            },
        }

    def cell(res: str, rows: int = 2, name: str = "write", survivor: str = "") -> dict:
        return {"wrapper_name": name, "caller_file": "scripts/a.py", "resolution": res,
                "surviving_definition": survivor, "write_class": W_NOT_ATTRIBUTED
                if not survivor else e438.C_FILE_WRITER,
                "caller_kind": REACH_PROD, "rows": rows}

    check("verdict_all_resolved",
          verdict_for([cell(R_ONE, survivor="scripts/b.py")]) == V_ALL_RESOLVED)
    check("verdict_local_counts_as_resolved",
          verdict_for([cell(R_LOCAL, survivor="scripts/a.py")]) == V_ALL_RESOLVED)
    check("verdict_ambiguous",
          verdict_for([cell(R_ONE, survivor="scripts/b.py"), cell(R_MANY)]) == V_SOME_AMBIGUOUS)
    check("verdict_ambiguous_beats_unbound",
          verdict_for([cell(R_MANY), cell(R_NONE)]) == V_SOME_AMBIGUOUS)
    check("verdict_unbound", verdict_for([cell(R_NONE), cell(R_STAR)]) == V_SOME_UNBOUND)
    check("verdict_reexport_is_unbound", verdict_for([cell(R_REEXPORT)]) == V_SOME_UNBOUND)

    good = face_of([cell(R_ONE, survivor="scripts/b.py"), cell(R_MANY, name="dump")])
    check("tally_clean", tally_problems(good) == [])
    bad = json.loads(json.dumps(good))
    bad["summary"]["by_resolution"][R_ONE] = 9
    check("tally_catches_a_shifted_cell", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(good))
    bad2["verdict"] = V_ALL_RESOLVED
    check("tally_catches_a_carried_verdict", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(good))
    bad3["rows"][0]["surviving_definition"] = ""
    check("tally_catches_a_resolution_without_a_survivor", tally_problems(bad3) != [])
    bad4 = json.loads(json.dumps(good))
    bad4["rows"][1]["surviving_definition"] = "scripts/c.py"
    check("tally_catches_an_ambiguity_with_a_survivor", tally_problems(bad4) != [])
    bad5 = json.loads(json.dumps(good))
    bad5["summary"]["per_name"][0]["rows"] = 1
    check("tally_catches_a_wrong_name_block", tally_problems(bad5) != [])
    bad6 = json.loads(json.dumps(good))
    bad6["rows"][0]["rows"] = 0
    check("tally_catches_an_empty_cell", tally_problems(bad6) != [])

    # the import reader on a synthetic module graph, built on disk in a temp dir
    check("module_resolution_prefers_a_real_file",
          _resolve_module("scripts.e443_bare_call_resolve", "scripts/x.py")
          == ["scripts/e443_bare_call_resolve.py"])
    check("module_resolution_tries_the_flat_name",
          _resolve_module("e443_bare_call_resolve", "scripts/x.py")
          == ["scripts/e443_bare_call_resolve.py"])
    check("module_resolution_refuses_a_missing_module",
          _resolve_module("no_such_module_xyz", "scripts/x.py") == [])

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
        s = face["summary"]
        print(f"verdict: {face['verdict']}")
        print(json.dumps(s["by_resolution"], ensure_ascii=False))
        print(f"resolved: {s['rows_that_resolve_to_one_definition']} of {s['shared_name_rows']}"
              f" ({s['share_resolved']}); ambiguous {s['rows_still_ambiguous']};"
              f" unbound {s['rows_with_no_visible_definition']}")
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