"""E437: measure the recall of the E428 name heuristic at the call row, not at the callee.

E434 counted 30 fixture-shaped parameter-directory write sites by applying E428's heuristic
(function or path contains fixture/_mk/_stub/_toy/write_fixture/_panel/_save) to the whole
population.  That number is a *name* test on the callee: a function that takes a temp directory
under a name that carries none of those words never enters it.

The obvious way to price the gap -- mark a site "temp" when its caller supplies a temp directory
-- is wrong, and the first draft of this study did it.  A generic helper (``dump``, ``save``,
``write_json``) that takes a directory has many callers, so one test passing ``tmp_path`` made the
*whole helper* temp-shaped and 108 of 112 "missed" rows were reported as reached from production;
they are ordinary repository writes that a test happens to call once.  The unit has to be the
call row: one caller, one argument text, one callee name.

So the population here is the directory-parameter call rows of the scan, and two labels are read
independently of each other:

  * temp -- the text that call row passes for the directory parameter contains a temp marker
    (E432's list: mkdtemp/temporarydirectory/tempfile/tmpdir/tmp_dir/tempdir/gettempdir).  The
    callee's name is not part of this test.
  * named -- E428's own word test on the callee (function or source path).

The missed cell is therefore "this call hands a temp directory to a function whose name carries
no fixture word", and the recall question is how much of the temp-supplying corpus that leaves.
Each missed call row is then priced by the caller's own kind (selftest/smoke vs product) and by
whether a reader in the corpus spells a name the callee composes.

A second, smaller gap is published alongside it: pytest's ``tmp_path`` is not in the marker list,
so a call that passes ``tmp_path`` is invisible to the temp label itself.  Those rows are counted
separately rather than folded in, because folding them in would be measuring a different word
list.

Usage:
    python scripts/e437_name_recall.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import date

import e428_no_caller as e428
import e429_two_hop_writer as e420
import e432_fixture_write as e432

ROOT = e420.ROOT
ST = e420.ST
E434_FACE = os.path.join(ST, "fixturebeyond_latest.json")
OUTDIR = ST

C_TEMP = e432.C_TEMP
C_REPO = e432.C_REPO
C_RUNTIME = e432.C_RUNTIME
C_NEVER = e432.C_NEVER
CLASS_VOCAB = e432.CLASS_VOCAB
R_OPENS = e432.R_OPENS
R_NO_READER = e432.R_NO_READER
READER_VOCAB = e432.READER_VOCAB
REACH_PROD = e432.REACH_PROD
REACH_TEST = e432.REACH_TEST
REACH_NONE = e432.REACH_NONE
REACH_VOCAB = e432.REACH_VOCAB
TEST_HINTS = e432.TEST_HINTS
TEMP_MARKERS = e432.TEMP_MARKERS
FIXTURE_WORDS = e428.FIXTURE_WORDS

# pytest's own fixture name, deliberately outside TEMP_MARKERS: it is published as a separate
# blind spot of the marker list rather than silently added to it.
PYTEST_TMP = ("tmp_path", "tmp_path_factory")

# Caller function names that read as a verification harness inside a production module.  This is a
# *published refinement* of E432's TEST_HINTS (which only matches selftest/test_/smoke/fixture), so
# it never changes the verdict -- it prices how much of the "product caller" bucket is really a
# verify()/reprice()/rerun() harness rather than a product path.
VERIFY_NAME_HINTS = ("verify", "reprice", "reading", "rerun", "stamp", "probe", "doctor",
                     "dryrun", "dry_run", "sweep", "selftest")

SHAPE_SELFTEST = "selftest_or_smoke_caller"
SHAPE_VERIFY = "verification_harness_function_in_a_production_module"
SHAPE_OTHER = "no_test_or_verify_hint_in_the_caller"
SHAPE_VOCAB = (SHAPE_SELFTEST, SHAPE_VERIFY, SHAPE_OTHER)

CELL_BOTH = "temp_directory_and_a_fixture_word_in_the_callee_name"
CELL_MISSED = "temp_directory_but_no_fixture_word_in_the_callee_name"
CELL_NAME_ONLY = "fixture_word_in_the_callee_name_but_no_temp_directory"
CELL_NEITHER = "neither_a_temp_directory_nor_a_fixture_word"
CELL_VOCAB = (CELL_BOTH, CELL_MISSED, CELL_NAME_ONLY, CELL_NEITHER)

V_EMPTY = "no_directory_parameter_call_row_in_the_scan"
V_NO_TEMP = ("no_call_row_in_the_corpus_supplies_a_temp_directory_so_the_name_heuristic_has"
             "_nothing_to_recall_against_here")
V_FULL_RECALL = "every_temp_supplying_call_row_names_a_fixture_shaped_callee"
V_MISSED_TEST_ONLY = ("the_temp_supplying_call_rows_the_name_heuristic_misses_are_made_from"
                      "_selftest_or_smoke_callers_only")
V_MISSED_PROD = ("some_temp_supplying_call_row_the_name_heuristic_misses_is_made_from_a_product"
                 "_caller")
VERDICT_VOCAB = (V_EMPTY, V_NO_TEMP, V_FULL_RECALL, V_MISSED_TEST_ONLY, V_MISSED_PROD)

POPULATION_KEYS = ("corpus_sources", "directory_parameter_call_rows")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list[str]:
    """E432's scope, minus this study's own files (self-inclusion law, E180/E207)."""
    return [p for p in e432.corpus()
            if not os.path.basename(p).startswith(("e437", "_e437", "run_e437"))]


def words_hit(site) -> list[str]:
    """Which fixture words the name heuristic matches on this callee (empty = missed)."""
    hay = " ".join([site.func, site.path]).lower()
    return [w for w in FIXTURE_WORDS if w in hay]


def is_temp_text(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in TEMP_MARKERS)


def is_directory_expression(text: str) -> bool:
    """A directory argument is one short expression, not a payload.

    The argument text is expanded through the caller's constants, and when the parameter position
    does not line up the expansion can return a whole JSON payload or a whole call.  A payload that
    happens to contain ``tempfile`` somewhere is not a call that passes a temp directory, so the
    marker test only counts on a single-line, short text.
    """
    text = text or ""
    return bool(text.strip()) and "\n" not in text and len(text) <= 220


def is_temp_call(text: str) -> bool:
    return is_temp_text(text) and is_directory_expression(text)


def is_pytest_tmp_text(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in PYTEST_TMP)


def caller_kind(row: dict) -> str:
    """Product or test, read from the caller's own file and function name."""
    hay = ((row.get("caller") or "") + " " + (row.get("file") or "")).lower()
    return REACH_TEST if any(h in hay for h in TEST_HINTS) else REACH_PROD


def caller_shape(row: dict) -> str:
    """The refinement published next to caller_kind; it never feeds the verdict."""
    func = (row.get("caller") or "").lower()
    if caller_kind(row) == REACH_TEST:
        return SHAPE_SELFTEST
    if any(h in func for h in VERIFY_NAME_HINTS):
        return SHAPE_VERIFY
    return SHAPE_OTHER


def cell_of(temp: bool, named: bool) -> str:
    if temp and named:
        return CELL_BOTH
    if temp:
        return CELL_MISSED
    if named:
        return CELL_NAME_ONLY
    return CELL_NEITHER


def verdict_for(rows: list[dict], tally: dict[str, int]) -> str:
    """Recomputed from the published rows and the cell tally, never carried."""
    if not tally:
        return V_EMPTY
    temp = tally.get(CELL_BOTH, 0) + tally.get(CELL_MISSED, 0)
    if temp == 0:
        return V_NO_TEMP
    if not rows:
        return V_FULL_RECALL
    if any(r["caller_kind"] == REACH_PROD for r in rows):
        return V_MISSED_PROD
    return V_MISSED_TEST_ONLY


def call_rows(param: list, index: dict) -> list[dict]:
    """Every (call row, directory argument text, callee) triple, de-duplicated.

    The same call line reaches a callee once per directory parameter; only one text per
    (caller file, caller function, line, callee) is kept so a two-parameter writer is not counted
    twice.
    """
    out: list[dict] = []
    seen: set[tuple] = set()
    for site in param:
        for row, arg in e432.supplied(site, index):
            key = (row.get("file"), row.get("caller"), row.get("line"), site.func)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "callee_file": site.path,
                "callee_function": site.func,
                "callee_line": site.line,
                "caller_file": row.get("file"),
                "caller_function": row.get("caller"),
                "caller_line": row.get("line"),
                "argument": arg,
                "directory_class": e432.directory_class([(row, arg)]),
                "name_words": words_hit(site),
            })
    return out


def build(cutoff: str | None = None) -> dict:
    cut = cutoff or _load(E434_FACE)["evidence_cutoff"]
    sources = corpus()
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print(f"stage: {len(param)} parameter sites over {len(sources)} sources", flush=True)
    rows_all = call_rows(param, index)
    print(f"stage: {len(rows_all)} directory-parameter call rows", flush=True)

    tally: dict[str, int] = {c: 0 for c in CELL_VOCAB}
    for r in rows_all:
        tally[cell_of(is_temp_call(r["argument"]), bool(r["name_words"]))] += 1

    missed = [r for r in rows_all
              if is_temp_call(r["argument"]) and not r["name_words"]]
    # the marker list's own blind spot: call rows that pass a pytest tmp path
    blind = [r for r in rows_all
             if is_pytest_tmp_text(r["argument"]) and is_directory_expression(r["argument"])]
    rejected_payload = [r for r in rows_all
                        if is_temp_text(r["argument"])
                        and not is_directory_expression(r["argument"])]

    wanted: set[str] = set()
    for r in missed:
        pass
    callee_by_key = {(s.path, s.func, s.line): s for s in param}
    for r in missed:
        site = callee_by_key.get((r["callee_file"], r["callee_function"], r["callee_line"]))
        if site is not None:
            wanted.update(e432.composed_names(site))
    readers = e432.reader_index(sources, wanted) if wanted else []

    published: list[dict] = []
    for r in missed:
        site = callee_by_key.get((r["callee_file"], r["callee_function"], r["callee_line"]))
        names = e432.composed_names(site) if site is not None else []
        opened = e432.readers_of(names, readers)
        # the callee's own reachability, priced with E432's instrument over all of its call sites
        site_pairs = e432.supplied(site, index) if site is not None else []
        published.append({
            "callee_file": r["callee_file"],
            "callee_function": r["callee_function"],
            "callee_line": r["callee_line"],
            "caller_file": r["caller_file"],
            "caller_function": r["caller_function"],
            "caller_line": r["caller_line"],
            "argument": r["argument"][:200],
            "caller_kind": caller_kind({"file": r["caller_file"],
                                        "caller": r["caller_function"]}),
            "caller_shape": caller_shape({"file": r["caller_file"],
                                          "caller": r["caller_function"]}),
            "callee_reach": e432.reachability(site_pairs, index) if site is not None else REACH_NONE,
            "reader": R_OPENS if opened else R_NO_READER,
            "composed_names": names,
            "reader_sites": opened,
            "name_words_matched": [],
        })
    published.sort(key=lambda r: (r["caller_kind"], r["caller_file"] or "",
                                  r["caller_line"] or 0))

    by_kind: dict[str, int] = {}
    for r in published:
        by_kind[r["caller_kind"]] = by_kind.get(r["caller_kind"], 0) + 1
    by_shape: dict[str, int] = {}
    for r in published:
        by_shape[r["caller_shape"]] = by_shape.get(r["caller_shape"], 0) + 1
    by_callee: dict[str, int] = {}
    for r in published:
        by_callee[r["callee_function"]] = by_callee.get(r["callee_function"], 0) + 1

    temp_total = tally[CELL_BOTH] + tally[CELL_MISSED]
    named_total = tally[CELL_BOTH] + tally[CELL_NAME_ONLY]
    blind_named = sum(1 for r in blind if r["name_words"])
    summary = {
        "corpus_sources": len(sources),
        "parameter_write_sites": len(param),
        "directory_parameter_call_rows": len(rows_all),
        "temp_supplying_call_rows": temp_total,
        "named_callee_call_rows": named_total,
        "cells": tally,
        "recall_over_the_temp_call_rows": (round(tally[CELL_BOTH] / temp_total, 4)
                                           if temp_total else None),
        "precision_over_the_named_call_rows": (round(tally[CELL_BOTH] / named_total, 4)
                                               if named_total else None),
        "missed_call_rows": len(published),
        "missed_distinct_callees": len(by_callee),
        "missed_by_caller_kind": by_kind,
        "missed_by_caller_shape": by_shape,
        "missed_from_a_product_caller": by_kind.get(REACH_PROD, 0),
        "missed_with_a_reader_that_spells_the_name": sum(1 for r in published
                                                         if r["reader"] == R_OPENS),
        "missed_top_callees": sorted(by_callee.items(), key=lambda kv: -kv[1])[:12],
        "temp_texts_rejected_as_payload": len(rejected_payload),
        "marker_list_blind_spot": {
            "marker_list": list(TEMP_MARKERS),
            "pytest_names_outside_the_list": list(PYTEST_TMP),
            "call_rows_passing_one_of_those_names": len(blind),
            "of_which_the_callee_name_is_fixture_shaped": blind_named,
            "of_which_the_callee_name_has_no_fixture_word": len(blind) - blind_named,
        },
        "population_premise": {
            "published_sentence": "30 fixture-shaped parameter-directory write sites (E434)",
            "measured": "E434 applied a name test to the callee; a site-level temp label would "
                        "inherit the same defect (one temp-passing caller marks a generic helper "
                        "temp), so the unit here is the call row and the 30 is published as "
                        "precision over the named call rows rather than as the temp population",
        },
    }
    return {
        "study": "E437_which_temp_directory_write_site_the_name_heuristic_misses",
        "card": "E437-WHICH-TEMP-DIRECTORY-WRITE-SITE-THE-NAME-HEURISTIC-MISSES",
        "title": "cross-cut the directory-parameter call rows by whether the row supplies a temp "
                 "directory and whether the callee's name carries a fixture word, and price the "
                 "rows only one of the two labels sees",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(published, tally),
        "cell_vocab": list(CELL_VOCAB),
        "class_vocab": list(CLASS_VOCAB),
        "reader_vocab": list(READER_VOCAB),
        "reach_vocab": list(REACH_VOCAB),
        "fixture_words": list(FIXTURE_WORDS),
        "population_keys": list(POPULATION_KEYS),
        "summary": summary,
        "rows": published,
        "method_limits": [
            "the unit is the call row: the same callee appears once per caller, so a number here "
            "counts call sites and never functions; the site-level count is in "
            "parameter_write_sites and the two must not be compared",
            "the temp label is a text test on the supplied argument (E432's marker list), so a "
            "caller that keeps a temp path in a variable whose name carries no marker is graded "
            "runtime_constant and lands outside the temp population; the pytest tmp_path rows are "
            "published as a separate blind-spot block for that reason",
            "the name label is E428's heuristic verbatim (same word list, same function/path "
            "haystack), so the recall measured is the recall of the published instrument",
            "caller_kind reads TEST_HINTS over the caller's file and function name: a helper "
            "module under a tests directory whose name carries no hint is graded product",
            "reader detection matches a composed name as a whole path segment; a reader that "
            "builds the name from parts does not match",
            "one call line reaches a two-parameter writer twice; only the first text per "
            "(caller file, caller function, line, callee) is kept",
        ],
    }


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    tally = s.get("cells") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    if face.get("verdict") != verdict_for(rows, tally):
        problems.append("verdict does not re-derive from the rows")
    if set(tally or {}) != set(CELL_VOCAB):
        problems.append("the cell tally does not carry every frozen cell")
    if sum((tally or {}).values()) != s.get("directory_parameter_call_rows"):
        problems.append("the cell tally does not add up to the directory-parameter call rows")
    if (tally.get(CELL_BOTH, 0) + tally.get(CELL_MISSED, 0)) != s.get("temp_supplying_call_rows"):
        problems.append("temp_supplying_call_rows does not re-derive from the cells")
    if (tally.get(CELL_BOTH, 0) + tally.get(CELL_NAME_ONLY, 0)) != s.get("named_callee_call_rows"):
        problems.append("named_callee_call_rows does not re-derive from the cells")
    if len(rows) != tally.get(CELL_MISSED):
        problems.append("row count does not equal the missed cell")
    by_kind: dict[str, int] = {}
    by_shape: dict[str, int] = {}
    for r in rows:
        if not is_temp_call(r.get("argument") or ""):
            problems.append("%s:%s is published as missed but its argument carries no temp marker"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("name_words_matched"):
            problems.append("%s:%s is published as missed but matched %r"
                            % (r.get("caller_file"), r.get("caller_line"),
                               r.get("name_words_matched")))
        if r.get("caller_kind") not in (REACH_PROD, REACH_TEST):
            problems.append("%s:%s: caller kind outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("caller_shape") not in SHAPE_VOCAB:
            problems.append("%s:%s: caller shape outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("caller_shape") == SHAPE_SELFTEST and r.get("caller_kind") != REACH_TEST:
            problems.append("%s:%s: a selftest shape published as a product caller"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("reader") not in READER_VOCAB:
            problems.append("%s:%s: reader outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("reader") == R_OPENS and not r.get("reader_sites"):
            problems.append("%s:%s: opens but no reader site named"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r.get("callee_reach") not in REACH_VOCAB:
            problems.append("%s:%s: callee reach outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
        by_kind[r.get("caller_kind")] = by_kind.get(r.get("caller_kind"), 0) + 1
        by_shape[r.get("caller_shape")] = by_shape.get(r.get("caller_shape"), 0) + 1
    if by_kind != (s.get("missed_by_caller_kind") or {}):
        problems.append("missed_by_caller_kind does not re-derive from the rows")
    if by_shape != (s.get("missed_by_caller_shape") or {}):
        problems.append("missed_by_caller_shape does not re-derive from the rows")
    if by_kind.get(REACH_PROD, 0) != s.get("missed_from_a_product_caller"):
        problems.append("missed_from_a_product_caller does not re-derive from the rows")
    if sum(1 for r in rows if r.get("reader") == R_OPENS) != \
            s.get("missed_with_a_reader_that_spells_the_name"):
        problems.append("the reader count does not re-derive from the rows")
    if len({r.get("callee_function") for r in rows}) != s.get("missed_distinct_callees"):
        problems.append("missed_distinct_callees does not re-derive from the rows")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, "namerecall_latest.json"))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    if live["summary"]["cells"] != face["summary"]["cells"]:
        problems.append("live cell tally differs from the published face")
    if (live["summary"]["directory_parameter_call_rows"]
            != face["summary"]["directory_parameter_call_rows"]):
        problems.append("live call-row count differs from the published face")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    row = {"caller_file": "scripts/x.py", "caller_function": "run", "caller_line": 1,
           "callee_file": "scripts/y.py", "callee_function": "dump", "callee_line": 2,
           "argument": "tmpdir", "caller_kind": REACH_TEST, "caller_shape": SHAPE_SELFTEST,
           "callee_reach": REACH_PROD,
           "reader": R_NO_READER, "reader_sites": [], "name_words_matched": [],
           "composed_names": []}
    full = {c: 0 for c in CELL_VOCAB}
    full[CELL_BOTH] = 3

    # Legs 1-6: verdict branches, all reachable, recomputed from rows + tally.
    check("empty population", verdict_for([], {}) == V_EMPTY)
    check("no temp supplied anywhere",
          verdict_for([], {**full, CELL_BOTH: 0, CELL_NAME_ONLY: 4}) == V_NO_TEMP)
    check("full recall", verdict_for([], full) == V_FULL_RECALL)
    check("missed from a test caller",
          verdict_for([dict(row)], {**full, CELL_MISSED: 1}) == V_MISSED_TEST_ONLY)
    check("missed from a product caller",
          verdict_for([dict(row, caller_kind=REACH_PROD)],
                      {**full, CELL_MISSED: 1}) == V_MISSED_PROD)
    check("one product caller is enough",
          verdict_for([dict(row), dict(row, caller_kind=REACH_PROD)],
                      {**full, CELL_MISSED: 2}) == V_MISSED_PROD)

    # Leg 7: the four cells partition the population.
    check("cells partition",
          cell_of(True, True) == CELL_BOTH and cell_of(True, False) == CELL_MISSED
          and cell_of(False, True) == CELL_NAME_ONLY and cell_of(False, False) == CELL_NEITHER)

    # Leg 8: the labels are independent instruments -- the temp label must not read the name.
    check("temp label ignores the callee name", is_temp_text("os.path.join(root, tmpdir)")
          and not is_temp_text("root"))
    check("pytest tmp_path is outside the marker list, on purpose",
          is_pytest_tmp_text("tmp_path") and not is_temp_text("tmp_path"))

    # Leg 9b: the payload guard -- the marker test only counts on a directory expression, because
    # an argument expansion can hand back a whole JSON payload that merely mentions tempfile.
    check("a one-line temp expression is a directory",
          is_temp_call('os.path.join(tempfile.mkdtemp(prefix="x"), "d")'))
    check("a multi-line payload that mentions tempfile is not a directory",
          not is_temp_call('{\n "note": "tempfile.mkdtemp"\n}'))
    check("a long single-line text is not a directory",
          not is_temp_call("tmpdir" + " " * 300))

    # Leg 9: a caller with a test hint is test, one without is product; both directions pinned.
    check("caller kind reads the caller, not the callee",
          caller_kind({"file": "tests/test_a.py", "caller": "t"}) == REACH_TEST
          and caller_kind({"file": "scripts/run.py", "caller": "main"}) == REACH_PROD)
    check("the callee name does not influence the caller kind",
          caller_kind({"file": "scripts/run_dump.py", "caller": "main",
                       "callee_file": "scripts/write_fixture_panel.py"}) == REACH_PROD
          and caller_kind({"file": "scripts/selftest_a.py", "caller": "selftest",
                           "callee_file": "scripts/dump_plain.py"}) == REACH_TEST)

    # Leg 9b: the refinement is published next to the verdict, never instead of it -- a verify()
    # harness is still a product caller for the frozen vocabulary, so the verdict is unchanged.
    check("a verify harness is shaped verify and kinded product",
          caller_shape({"file": "scripts/e328_x.py", "caller": "verify"}) == SHAPE_VERIFY
          and caller_kind({"file": "scripts/e328_x.py", "caller": "verify"}) == REACH_PROD)
    check("a plain product function is shaped other",
          caller_shape({"file": "scripts/run.py", "caller": "main"}) == SHAPE_OTHER)
    check("the shapes partition every row",
          {caller_shape({"file": "a/test_x.py", "caller": "t"}),
           caller_shape({"file": "a/x.py", "caller": "verify"}),
           caller_shape({"file": "a/x.py", "caller": "main"})} == set(SHAPE_VOCAB))

    base = {"rows": [dict(row)], "verdict": V_MISSED_TEST_ONLY,
            "summary": {"cells": {**full, CELL_MISSED: 1},
                        "directory_parameter_call_rows": 4, "temp_supplying_call_rows": 4,
                        "named_callee_call_rows": 3,
                        "missed_by_caller_kind": {REACH_TEST: 1},
                        "missed_by_caller_shape": {SHAPE_SELFTEST: 1},
                        "missed_from_a_product_caller": 0,
                        "missed_with_a_reader_that_spells_the_name": 0,
                        "missed_distinct_callees": 1}}

    # Leg 10: a clean tally passes; a tally that does not add up is a problem.
    check("clean tally passes", not tally_problems(base))
    broken = json.loads(json.dumps(base))
    broken["summary"]["directory_parameter_call_rows"] = 5
    check("tally that does not add up is caught", bool(tally_problems(broken)))

    # Leg 11: the whole claim is "this row does not supply a temp"; a row that does not is a
    # mislabel (this is the check that catches a site-level aggregation creeping back in).
    broken = json.loads(json.dumps(base))
    broken["rows"][0]["argument"] = "os.path.join(ROOT, 'results')"
    check("a non-temp row in the missed list is caught", bool(tally_problems(broken)))

    # Leg 12: a row that actually matched a fixture word cannot be published as missed.
    broken = json.loads(json.dumps(base))
    broken["rows"][0]["name_words_matched"] = ["fixture"]
    check("a row that matched a fixture word is caught", bool(tally_problems(broken)))

    # Leg 13: a stored verdict that no longer follows from the rows is caught.
    broken = json.loads(json.dumps(base))
    broken["verdict"] = V_FULL_RECALL
    check("a verdict that does not re-derive is caught", bool(tally_problems(broken)))

    # Leg 14: the callee count is derived, not carried.
    broken = json.loads(json.dumps(base))
    broken["summary"]["missed_distinct_callees"] = 2
    check("a callee count that does not re-derive is caught", bool(tally_problems(broken)))

    # Leg 15: words_hit agrees with the imported instrument (no second copy of the word list).
    class _S:
        func = "write_fixture_csv"
        path = "scripts/x.py"

    class _S2:
        func = "dump_rows"
        path = "scripts/x.py"
    check("words_hit agrees with E428's own verdict",
          bool(words_hit(_S)) and not words_hit(_S2)
          and e428._fixture_shaped(_S) and not e428._fixture_shaped(_S2))

    # Leg 16: the marker list and the pytest blind spot are disjoint, so the two counts are not
    # the same rows counted twice.
    check("the blind-spot names are not also markers",
          not any(is_temp_text(n) for n in PYTEST_TMP))

    for f in fails:
        print(f"[FAIL] {f}")
    print(f"selftest {legs - len(fails)}/{legs}")
    return 0 if not fails else 1


def write_face(face: dict) -> str:
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    name = f"NAMERECALL-{face['evidence_cutoff']}.json"
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for target in (os.path.join(OUTDIR, name),
                   os.path.join(OUTDIR, "namerecall_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
    return os.path.join(OUTDIR, name)


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("[PROBLEM]", p)
        print(f"verify problems={len(problems)}")
        return 0 if not problems else 1
    face = build()
    path = write_face(face)
    s = face["summary"]
    print(f"published {_rel(path)}")
    print(f"verdict={face['verdict']}")
    print(f"sites={s['parameter_write_sites']} call_rows={s['directory_parameter_call_rows']} "
          f"temp={s['temp_supplying_call_rows']} named={s['named_callee_call_rows']} "
          f"missed={s['missed_call_rows']}")
    print(f"cells={s['cells']}")
    print(f"recall={s['recall_over_the_temp_call_rows']} "
          f"precision={s['precision_over_the_named_call_rows']}")
    print(f"missed_by_kind={s['missed_by_caller_kind']}")
    print(f"blind_spot={s['marker_list_blind_spot']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))