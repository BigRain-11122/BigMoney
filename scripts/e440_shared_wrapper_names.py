"""E440: the 24,911 rows E439 dropped were dropped by a reachability rule, not by a measurement.

E439 kept 40 of its call rows because "the caller file must be the defining module or a module
that imports it", and reported the other 24,911 as *overstated*.  That word is a claim, not a
reading: a dropped row can be a method call that happens to share the wrapper's name
(`f.write(x)`, `lst.append(x)`, `pool.run()`), or it can be a genuine call to a wrapper name that
more than one module defines.  Those two are opposite facts -- one says the name index invented the
row, the other says the tree has ambiguous helper names -- and E439 published neither.

So this study grades every dropped row on two independent axes, both read from source, neither
inferred from the other:

  axis 1 -- how many modules define this name (E439's definition scan, imported)
            one_definition / more_than_one_definition
  axis 2 -- how the call is spelled at its own line (re-parsed from the caller's AST)
            attribute_qualified (something.name(...)) / bare_name (name(...))
            / both_at_that_line / not_found_at_that_line

A row whose call is attribute-qualified is not evidence about a module-level wrapper: the receiver
is an object.  A row that is a bare call to a name with exactly one definition is the residue the
reachability rule threw away and cannot justify -- that is the population this study exists to
size, and it is published as `residue` rather than folded into either side.

Usage:
    python scripts/e440_shared_wrapper_names.py run|verify|selftest
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

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST
CARD = e439.CARD
FACE_NAME = "sharedname_latest.json"
DATED_PREFIX = "SHAREDNAME"

REACH_PROD = e432.REACH_PROD
REACH_TEST = e432.REACH_TEST

D_ONE = "one_definition_in_the_corpus"
D_MANY = "more_than_one_definition_in_the_corpus"
DEF_VOCAB = (D_ONE, D_MANY)

S_ATTR = "attribute_qualified_so_the_receiver_is_an_object"
S_BARE = "bare_name_at_its_own_line"
S_BOTH = "both_spellings_at_that_line"
S_MISSING = "the_call_is_not_at_that_line_in_the_live_file"
SPELL_VOCAB = (S_ATTR, S_BARE, S_BOTH, S_MISSING)

R_METHOD = "shadow_a_method_call_on_some_object"
R_SHARED = "shadow_a_bare_call_to_a_name_more_than_one_module_defines"
R_RESIDUE = "shadow_a_bare_call_to_a_name_with_a_single_definition"
R_UNSEEN = "shadow_the_call_is_not_at_that_line_any_more"
ROW_CLASSES = (R_METHOD, R_SHARED, R_RESIDUE, R_UNSEEN)

V_NO_SHADOW = "no_call_row_falls_outside_the_reach_of_its_wrapper"
V_SOME_RESIDUE = "some_dropped_rows_are_bare_calls_to_a_name_with_a_single_definition"
V_ALL_EXPLAINED = ("every_dropped_row_is_either_a_method_call_or_a_bare_call_to_a_name_that_more"
                   "_than_one_module_defines")
VERDICT_VOCAB = (V_NO_SHADOW, V_ALL_EXPLAINED, V_SOME_RESIDUE)

_AST_CACHE: dict[str, dict[tuple[int, str], int] | None] = {}


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


def _spellings(rel: str) -> dict[tuple[int, str], int] | None:
    """(line, name) -> {attribute, bare} seen in this file, parsed once and cached.

    24,911 rows over a few hundred files: walking the tree once per file and indexing the calls
    turns the per-row question into a dictionary hit instead of a fresh ast.walk.
    """
    if rel in _AST_CACHE:
        return _AST_CACHE[rel]
    try:
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        _AST_CACHE[rel] = None
        return None
    found: dict[tuple[int, str], int] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        lineno = getattr(node, "lineno", -1)
        func = node.func
        if isinstance(func, ast.Attribute):
            key = (lineno, func.attr)
            found[key] = found.get(key, 0) | 1
        elif isinstance(func, ast.Name):
            key = (lineno, func.id)
            found[key] = found.get(key, 0) | 2
    _AST_CACHE[rel] = found
    return found


def spelling_at(rel: str, line: int, name: str) -> str:
    """How the call to `name` is written at this exact line of this exact file.

    Read from the caller's own AST rather than from the name index that produced the row: the
    index files a row under a callee name, and `obj.write(p)` arrives there indistinguishable from
    `write(p)`.  That difference is the whole question.
    """
    found = _spellings(rel)
    if found is None:
        return S_MISSING
    bits = found.get((line, name), 0)
    if bits == 3:
        return S_BOTH
    if bits == 1:
        return S_ATTR
    if bits == 2:
        return S_BARE
    return S_MISSING


def row_class(def_axis: str, spell: str) -> str:
    """One class per dropped row, from the two axes, in an order that cannot double count."""
    if spell == S_MISSING:
        return R_UNSEEN
    if spell == S_ATTR:
        # an attribute call names a receiver; a module-level wrapper is not that receiver
        return R_METHOD
    if def_axis == D_MANY:
        return R_SHARED
    return R_RESIDUE


def verdict_for(rows: list[dict]) -> str:
    """Recomputed from the published row classes, never carried."""
    if not rows:
        return V_NO_SHADOW
    if any(r["row_class"] == R_RESIDUE for r in rows):
        return V_SOME_RESIDUE
    return V_ALL_EXPLAINED

def build(cutoff: str | None = None) -> dict:
    face438 = _load(CARD)
    cut = cutoff or face438["evidence_cutoff"]
    wrappers = e439.wrapper_rows(face438)
    names = sorted({f for _p, f in wrappers})
    sources = [p for p in e437.corpus()
               if not os.path.basename(p).startswith(("e440", "_e440", "run_e440"))]
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print(f"stage: {len(param)} parameter sites over {len(sources)} sources", flush=True)

    checks = e439.recheck(face438, param)
    confirmed = {(c["callee_file"], c["callee_function"]) for c in checks
                 if c["recheck"] == e439.R_CONFIRMED}
    defs = e439.definition_counts(names, sources)
    reach = {(p, f): set(e439.reachable_callers(p, sources)) for p, f in wrappers}
    print(f"stage: {len(confirmed)}/{len(wrappers)} wrappers confirmed live; "
          f"definitions " + ", ".join("%s=%d" % (n, len(defs.get(n) or [])) for n in names),
          flush=True)

    rows_all = e437.call_rows(param, index)
    by_key: dict[str, int] = {}
    shadow: list[dict] = []
    attributed = 0
    for r in rows_all:
        key = (r["callee_file"], r["callee_function"])
        if key not in confirmed:
            continue
        name = r["callee_function"]
        by_key[name] = by_key.get(name, 0) + 1
        if r["caller_file"] in reach[key]:
            attributed += 1
            continue
        n_defs = len(defs.get(name) or [])
        axis = D_ONE if n_defs <= 1 else D_MANY
        spell = spelling_at(r["caller_file"], r["caller_line"], name)
        shadow.append({
            "wrapper_name": name,
            "wrapper_file": r["callee_file"],
            "caller_file": r["caller_file"],
            "caller_function": r["caller_function"],
            "caller_line": r["caller_line"],
            "definition_axis": axis,
            "spelling": spell,
            "row_class": row_class(axis, spell),
            "caller_kind": e437.caller_kind({"file": r["caller_file"],
                                             "caller": r["caller_function"]}),
        })
    print(f"stage: {len(shadow)} dropped rows of {attributed + len(shadow)}", flush=True)

    # one published row per (name, caller file, spelling, axis, kind): the dropped mass is 25k
    # call lines and the finding is about names, so the face carries the cells plus a sample.
    cells: dict[tuple, int] = {}
    for r in shadow:
        k = (r["wrapper_name"], r["caller_file"], r["spelling"], r["definition_axis"],
             r["row_class"], r["caller_kind"])
        cells[k] = cells.get(k, 0) + 1
    published = [{"wrapper_name": k[0], "caller_file": k[1], "spelling": k[2],
                  "definition_axis": k[3], "row_class": k[4], "caller_kind": k[5],
                  "rows": v} for k, v in sorted(cells.items())]

    per_name = []
    for name in names:
        mine = [r for r in published if r["wrapper_name"] == name]
        total = sum(r["rows"] for r in mine)
        per_name.append({
            "name": name,
            "wrapper_files": sorted(p for p, f in wrappers if f == name),
            "definitions": len(defs.get(name) or []),
            "defining_files": sorted(defs.get(name) or []),
            "rows_by_the_name_index": by_key.get(name, 0),
            "rows_attributed": by_key.get(name, 0) - total,
            "shadow_rows": total,
            "shadow_by_row_class": _tally(mine, "row_class", ROW_CLASSES),
            "residue_rows": sum(r["rows"] for r in mine if r["row_class"] == R_RESIDUE),
            "caller_files_in_the_shadow": len(sorted({r["caller_file"] for r in mine})),
        })

    by_class = _tally(shadow, "row_class", ROW_CLASSES)
    residue = [r for r in shadow if r["row_class"] == R_RESIDUE]
    e439_dropped = (face439_summary().get("attribution") or {}).get("rows_dropped")
    summary = {
        "corpus_sources": len(sources),
        "wrappers_priced": len(confirmed),
        "distinct_wrapper_names": len(names),
        "names_defined_more_than_once": sum(1 for b in per_name if b["definitions"] > 1),
        "names_with_one_definition": sum(1 for b in per_name if b["definitions"] <= 1),
        "rows_by_the_name_index": sum(by_key.values()),
        "rows_attributed": attributed,
        "shadow_rows": len(shadow),
        "shadow_by_row_class": by_class,
        "shadow_by_spelling": _tally(shadow, "spelling", SPELL_VOCAB),
        "shadow_by_definition_axis": _tally(shadow, "definition_axis", DEF_VOCAB),
        "shadow_production_rows": sum(1 for r in shadow if r["caller_kind"] == REACH_PROD),
        "shadow_test_rows": sum(1 for r in shadow if r["caller_kind"] == REACH_TEST),
        "residue_rows": by_class.get(R_RESIDUE, 0),
        "share_of_shadow_that_is_residue": (round(by_class[R_RESIDUE] / len(shadow), 4)
                                            if shadow else None),
        "residue_names": sorted({r["wrapper_name"] for r in residue}),
        "residue_caller_files": len({r["caller_file"] for r in residue}),
        "per_name": per_name,
        "distance_check": {
            "e439_rows_dropped": e439_dropped,
            "recomputed_dropped": len(shadow),
            "agrees": e439_dropped == len(shadow),
            "reading": "the same rows, re-read on two axes instead of called overstated",
        },
    }
    return {
        "study": "E440_which_dropped_call_row_is_evidence_about_its_wrapper_name",
        "card": "E440-WHICH-WRAPPER-NAME-IS-SHARED-BY-MORE-THAN-ONE-DEFINITION",
        "title": "grade every call row E439 dropped by reachability on two read axes -- how many "
                 "modules define the name, and whether the call is attribute-qualified at its "
                 "own line -- and publish the residue neither axis explains",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(published),
        "definition_vocab": list(DEF_VOCAB),
        "spelling_vocab": list(SPELL_VOCAB),
        "row_classes": list(ROW_CLASSES),
        "summary": summary,
        "rows": published,
        "residue_examples": [
            {"wrapper_name": r["wrapper_name"], "caller_file": r["caller_file"],
             "caller_function": r["caller_function"], "caller_line": r["caller_line"]}
            for r in residue[:40]
        ],
        "method_limits": [
            "definition counts are per file that contains a top-level def of the name; a file "
            "defining the same name twice counts once, and a name that only ever exists as a "
            "method counts zero -- so 'one_definition' means 'at most one module defines it', "
            "not 'the name is unique in the tree'",
            "the second axis reads the caller's live source at the row's own line: a file that "
            "has changed since the row was indexed reports not_found_at_that_line and is classed "
            "unseen rather than assumed either way",
            "an attribute call is classed as a method call on the strength of its spelling only; "
            "the receiver's type is not inferred, so a module object reached through an alias "
            "reads as attribute_qualified",
            "the population is E439's wrapper set re-confirmed live; a wrapper whose call rows "
            "were dropped for any other reason is outside this face",
            "residue is a floor: a bare call to a single-definition name may still be a local "
            "function that shadows nothing, and this scan cannot see local scope",
        ],
    }


def face439_summary() -> dict:
    try:
        return (_load(os.path.join(OUTDIR, e439.FACE_NAME)).get("summary") or {})
    except (OSError, ValueError):
        return {}


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
    tally: dict[str, int] = {c: 0 for c in ROW_CLASSES}
    for r in rows:
        if r.get("row_class") not in ROW_CLASSES:
            problems.append("%s:%s class outside the vocabulary" % (r.get("wrapper_name"),
                                                                   r.get("caller_file")))
            continue
        if r.get("spelling") not in SPELL_VOCAB:
            problems.append("%s:%s spelling outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
        if r.get("definition_axis") not in DEF_VOCAB:
            problems.append("%s:%s definition axis outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
        if r.get("caller_kind") not in (REACH_PROD, REACH_TEST):
            problems.append("%s:%s caller kind outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
        if not isinstance(r.get("rows"), int) or r.get("rows") <= 0:
            problems.append("%s:%s carries a non-positive cell count"
                            % (r.get("wrapper_name"), r.get("caller_file")))
            continue
        if row_class(r["definition_axis"], r["spelling"]) != r["row_class"]:
            problems.append("%s:%s class does not re-derive from its own axes"
                            % (r.get("wrapper_name"), r.get("caller_file")))
        tally[r["row_class"]] = tally.get(r["row_class"], 0) + r["rows"]
    if tally != (s.get("shadow_by_row_class") or {}):
        problems.append("shadow_by_row_class does not re-derive from the rows")
    if sum(tally.values()) != s.get("shadow_rows"):
        problems.append("the class tally does not close against shadow_rows")
    if verdict_for(rows) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the published rows")
    per = s.get("per_name") or []
    if len(per) != s.get("distinct_wrapper_names"):
        problems.append("per_name does not cover every wrapper name")
    for block in per:
        mine = [r for r in rows if r.get("wrapper_name") == block.get("name")]
        if block.get("shadow_rows") != sum(r["rows"] for r in mine):
            problems.append("%s: shadow_rows does not re-derive" % block.get("name"))
        if block.get("residue_rows") != sum(r["rows"] for r in mine
                                            if r.get("row_class") == R_RESIDUE):
            problems.append("%s: residue_rows does not re-derive" % block.get("name"))
        if block.get("rows_attributed", 0) + block.get("shadow_rows", 0) \
                != block.get("rows_by_the_name_index"):
            problems.append("%s: kept plus shadow does not close against the name index"
                            % block.get("name"))
        axis_want = D_MANY if block.get("definitions", 0) > 1 else D_ONE
        if any(r["definition_axis"] != axis_want for r in mine):
            problems.append("%s: a row disagrees with its own definition count"
                            % block.get("name"))
    if sum(b.get("shadow_rows", 0) for b in per) != s.get("shadow_rows"):
        problems.append("the per-name blocks do not add up to the shadow total")
    if sum(b.get("rows_attributed", 0) for b in per) != s.get("rows_attributed"):
        problems.append("the per-name attributed counts do not add up")
    many = sum(1 for b in per if b.get("definitions", 0) > 1)
    if many != s.get("names_defined_more_than_once"):
        problems.append("names_defined_more_than_once does not re-derive")
    prod = sum(r["rows"] for r in rows if r.get("caller_kind") == REACH_PROD)
    if prod != s.get("shadow_production_rows"):
        problems.append("shadow_production_rows does not re-derive")
    if sum(r["rows"] for r in rows) != s.get("shadow_rows"):
        problems.append("the row cells do not close against shadow_rows")
    if (s.get("distance_check") or {}).get("recomputed_dropped") != s.get("shadow_rows"):
        problems.append("distance_check does not restate the shadow total")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    for key in ("shadow_rows", "rows_attributed", "shadow_by_row_class",
                "names_defined_more_than_once", "residue_rows"):
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

    check("class_method", row_class(D_MANY, S_ATTR) == R_METHOD)
    check("class_method_beats_a_shared_name", row_class(D_ONE, S_ATTR) == R_METHOD)
    check("class_shared", row_class(D_MANY, S_BARE) == R_SHARED)
    check("class_residue", row_class(D_ONE, S_BARE) == R_RESIDUE)
    check("class_both_on_a_shared_name", row_class(D_MANY, S_BOTH) == R_SHARED)
    check("class_both_on_a_single_definition", row_class(D_ONE, S_BOTH) == R_RESIDUE)
    check("class_unseen", row_class(D_ONE, S_MISSING) == R_UNSEEN)
    check("class_unseen_beats_the_axis", row_class(D_MANY, S_MISSING) == R_UNSEEN)
    check("verdict_empty", verdict_for([]) == V_NO_SHADOW)
    check("verdict_all_explained",
          verdict_for([{"row_class": R_METHOD}, {"row_class": R_SHARED}]) == V_ALL_EXPLAINED)
    check("verdict_residue", verdict_for([{"row_class": R_METHOD},
                                          {"row_class": R_RESIDUE}]) == V_SOME_RESIDUE)
    check("verdict_unseen_is_not_residue",
          verdict_for([{"row_class": R_UNSEEN}]) == V_ALL_EXPLAINED)

    def face_of(rows: list[dict]) -> dict:
        per = []
        for name in sorted({r["wrapper_name"] for r in rows} or {"save"}):
            mine = [r for r in rows if r["wrapper_name"] == name]
            defs = 2 if any(r["definition_axis"] == D_MANY for r in mine) else 1
            shadow = sum(r["rows"] for r in mine)
            per.append({"name": name, "definitions": defs, "shadow_rows": shadow,
                        "residue_rows": sum(r["rows"] for r in mine
                                            if r["row_class"] == R_RESIDUE),
                        "rows_attributed": 1, "rows_by_the_name_index": shadow + 1,
                        "shadow_by_row_class": _tally(mine, "row_class", ROW_CLASSES),
                        "caller_files_in_the_shadow": 1})
        return {
            "verdict": verdict_for(rows),
            "rows": rows,
            "summary": {
                "shadow_rows": sum(r["rows"] for r in rows),
                "rows_attributed": sum(b["rows_attributed"] for b in per),
                "shadow_by_row_class": {k: sum(r.get("rows", 1) for r in rows
                                               if r["row_class"] == k)
                                        for k in ROW_CLASSES},
                "shadow_production_rows": sum(r["rows"] for r in rows
                                              if r["caller_kind"] == REACH_PROD),
                "shadow_test_rows": sum(r["rows"] for r in rows
                                        if r["caller_kind"] == REACH_TEST),
                "residue_rows": sum(r["rows"] for r in rows if r["row_class"] == R_RESIDUE),
                "distinct_wrapper_names": len(per),
                "names_defined_more_than_once": sum(1 for b in per if b["definitions"] > 1),
                "per_name": per,
                "distance_check": {"recomputed_dropped": sum(r["rows"] for r in rows)},
            },
        }

    cell = {"wrapper_name": "save", "caller_file": "scripts/a.py", "spelling": S_BARE,
            "definition_axis": D_ONE, "row_class": R_RESIDUE, "caller_kind": REACH_PROD,
            "rows": 3}
    good = face_of([cell, dict(cell, row_class=R_METHOD, spelling=S_ATTR, rows=5,
                              caller_file="scripts/b.py")])
    check("tally_clean", tally_problems(good) == [])
    bad = json.loads(json.dumps(good))
    bad["summary"]["shadow_by_row_class"][R_RESIDUE] = 99
    check("tally_catches_a_shifted_cell", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(good))
    bad2["rows"][0]["row_class"] = R_METHOD
    check("tally_catches_a_carried_class", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(good))
    bad3["verdict"] = V_ALL_EXPLAINED
    check("tally_catches_a_carried_verdict", tally_problems(bad3) != [])
    bad4 = json.loads(json.dumps(good))
    bad4["rows"][0]["rows"] = 0
    check("tally_catches_an_empty_cell", tally_problems(bad4) != [])
    bad5 = json.loads(json.dumps(good))
    bad5["summary"]["per_name"][0]["shadow_rows"] = 1
    check("tally_catches_a_wrong_name_block", tally_problems(bad5) != [])
    bad6 = json.loads(json.dumps(good))
    bad6["rows"][0]["definition_axis"] = D_MANY
    check("tally_catches_a_row_that_contradicts_its_name", tally_problems(bad6) != [])

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
        print(json.dumps(s["shadow_by_row_class"], ensure_ascii=False))
        print(f"residue: {s['residue_rows']} of {s['shadow_rows']} dropped rows "
              f"({s['share_of_shadow_that_is_residue']})")
        print(f"names: {s['names_defined_more_than_once']} of {s['distinct_wrapper_names']} "
              f"defined by more than one module")
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
