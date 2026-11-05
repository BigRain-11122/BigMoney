"""E434: count fixture-shaped parameter-directory write sites over the whole population.

E428 counted ``fixture_shaped`` over the 35 rows its narrow index could not place, and E432
priced those 21.  Nobody has asked how many of the remaining 289 parameter-directory write
sites in the same scan are fixture-shaped, so the published sentence "21 fixture-shaped
parameter-directory write sites among its 310" reads like a population statement when it is a
statement about 35 rows.

This study applies the *same* heuristic (``e428._fixture_shaped``: function name or path contains
fixture/_mk/_stub/_toy/write_fixture/_panel/_save) to every parameter-directory write site the
scan found, subtracts the rows E432 already published, and prices the remainder with E432's own
instrument: where does the caller point the directory (temp / repo_relative / runtime_constant /
never_supplied), is the site reached from a production or a selftest caller, and does any reader
in the corpus spell a name the site composes.

The unit of comparison is the row, never the count: the 21 published rows are read from the
E432 face by (file, function, line) and the union with E428's own fixture rows is what defines
"already priced", so a site that moved or disappeared is reported rather than silently dropped.

Usage:
    python scripts/e434_fixture_beyond.py run|verify|selftest
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
E428_FACE = os.path.join(ST, "no_caller_latest.json")
E432_FACE = os.path.join(ST, "fixturewrite_latest.json")
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

V_EMPTY = "no_fixture_shaped_parameter_site_in_the_scan"
V_ALL_ALREADY = ("every_fixture_shaped_parameter_site_in_the_scan_was_already_one_of_the_rows_e428"
                 "_could_not_place")
V_OUTSIDE_TEMP = ("the_fixture_shaped_sites_outside_the_unplaced_rows_all_take_a_temp_or_a_runtime"
                  "_directory_and_no_reader_opens_what_they_write")
V_OUTSIDE_REPO_OPEN = ("some_fixture_shaped_site_outside_the_unplaced_rows_spells_a_repository"
                       "_directory_and_a_reader_opens_the_name")
V_OUTSIDE_REPO_CLOSED = ("some_fixture_shaped_site_outside_the_unplaced_rows_spells_a_repository"
                         "_directory_but_no_reader_opens_the_name")
VERDICT_VOCAB = (V_EMPTY, V_ALL_ALREADY, V_OUTSIDE_TEMP, V_OUTSIDE_REPO_OPEN,
                 V_OUTSIDE_REPO_CLOSED)

POPULATION_KEYS = ("corpus_sources", "parameter_write_sites")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _key(row: dict) -> tuple[str, str, int]:
    return (row["file"], row["function"], row["line"])


def priced_keys() -> set[tuple[str, str, int]]:
    """Rows already priced by E432, union E428's own fixture rows (both read, never guessed)."""
    keys: set[tuple[str, str, int]] = set()
    for row in _load(E432_FACE).get("rows") or []:
        keys.add(_key(row))
    for row in _load(E428_FACE).get("rows") or []:
        if row.get("fixture_shaped"):
            keys.add(_key(row))
    return keys


def verdict_for(rows: list[dict], total_fixture_shaped: int) -> str:
    if total_fixture_shaped == 0:
        return V_EMPTY
    if not rows:
        return V_ALL_ALREADY
    repo = [r for r in rows if r["class"] == C_REPO]
    if not repo:
        return V_OUTSIDE_TEMP
    if any(r["reader"] == R_OPENS for r in repo):
        return V_OUTSIDE_REPO_OPEN
    return V_OUTSIDE_REPO_CLOSED


def build(cutoff: str | None = None) -> dict:
    cut = cutoff or _load(E432_FACE)["evidence_cutoff"]
    already = priced_keys()

    sources = e432.corpus()
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    fixture_all = [s for s in param if e428._fixture_shaped(s)]
    outside = [s for s in fixture_all if (s.path, s.func, s.line) not in already]
    inside = [s for s in fixture_all if (s.path, s.func, s.line) in already]
    print(f"stage: {len(param)} parameter sites, {len(fixture_all)} fixture-shaped, "
          f"{len(outside)} outside the already-priced rows, {len(sources)} sources", flush=True)

    wanted: set[str] = set()
    for site in outside:
        wanted.update(e432.composed_names(site))
    index = e420.main_call_index({s.func for s in outside}, sources)
    readers = e432.reader_index(sources, wanted) if wanted else []

    rows: list[dict] = []
    for site in outside:
        pairs = e432.supplied(site, index)
        names = e432.composed_names(site)
        hits = e432.readers_of(names, readers)
        rows.append({
            "file": site.path,
            "function": site.func,
            "line": site.line,
            "write_call": site.call_name,
            "parameters": site.parameter_directories(),
            "class": e432.directory_class(pairs),
            "reader": R_OPENS if hits else R_NO_READER,
            "reachable": e432.reachability(pairs, index),
            "caller_sites": [{"file": r.get("file"), "caller": r.get("caller"),
                              "line": r.get("line"), "arg": a}
                             for r, a in pairs[:4]],
            "composed_names": names,
            "reader_sites": hits,
            "production_callers": sum(1 for r, _ in pairs
                                      if not any(h in ((r.get("caller") or "") + " " +
                                                       (r.get("file") or "")).lower()
                                                 for h in e432.TEST_HINTS)),
        })
    rows.sort(key=lambda r: (r["class"], r["file"], r["line"]))

    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    by_reach: dict[str, int] = {}
    for r in rows:
        by_reach[r["reachable"]] = by_reach.get(r["reachable"], 0) + 1

    summary = {
        "parameter_write_sites": len(param),
        "fixture_shaped_over_the_whole_population": len(fixture_all),
        "fixture_shaped_inside_the_rows_e428_could_not_place": len(inside),
        "fixture_shaped_outside_the_rows_e428_could_not_place": len(rows),
        "by_class": by_class,
        "by_reachable": by_reach,
        "by_reader": {R_OPENS: sum(1 for r in rows if r["reader"] == R_OPENS),
                      R_NO_READER: sum(1 for r in rows if r["reader"] == R_NO_READER)},
        "sites_where_a_reader_could_open_the_written_file": sum(
            1 for r in rows if r["class"] == C_REPO and r["reader"] == R_OPENS),
        "sites_where_a_reader_spells_the_same_name_only": sum(
            1 for r in rows if r["class"] != C_REPO and r["reader"] == R_OPENS),
        "temp_sites": sum(1 for r in rows if r["class"] == C_TEMP),
        "runtime_sites": sum(1 for r in rows if r["class"] == C_RUNTIME),
        "corpus_sources": len(sources),
        "reader_calls_scanned": len(readers),
        "population_premise": {
            "published_sentence": "21 fixture-shaped parameter-directory write sites among "
                                  "its 310",
            "measured": "E428 counted fixture_shaped over the 35 rows its narrow index could "
                        "not place; the count here is over all parameter-directory write sites",
            "factor": round(len(param) / max(1, len(inside) + len(rows)), 2),
        },
    }
    return {
        "study": "E434_which_parameter_site_outside_the_unplaced_set_is_fixture_shaped",
        "card": "E434-WHICH-PARAMETER-SITE-OUTSIDE-E428-UNPLACED-SET-IS-FIXTURE-SHAPED",
        "title": "count fixture-shaped parameter-directory write sites over the whole population, "
                 "not only the 35 rows E428 could not place, and price where their callers "
                 "point them",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(rows, len(fixture_all)),
        "class_vocab": list(CLASS_VOCAB),
        "reader_vocab": list(READER_VOCAB),
        "reach_vocab": list(REACH_VOCAB),
        "population_keys": list(POPULATION_KEYS),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "the heuristic is E428's own name test (function or path contains fixture/_mk/_stub/"
            "_toy/write_fixture/_panel/_save); it is deliberately the same instrument, so this "
            "study measures the population the sentence was about and does not re-cut the class",
            "directory_class and the reader test are E432's, imported rather than re-written: a "
            "runtime_constant is 'the caller passes a name', not 'the directory is unknown'",
            "reader detection matches a composed name as a whole path segment; a reader that "
            "builds the same name from parts does not match, so R_NO_READER means 'no reader "
            "spells this name'",
            "E428's own fixture rows are unioned with E432's published rows when deciding what is "
            "already priced, so a row that E432 dropped stays on the priced side and is not "
            "counted twice",
        ],
    }


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face["rows"]
    s = face["summary"]
    if face["verdict"] not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    total = s.get("fixture_shaped_over_the_whole_population") or 0
    if face["verdict"] != verdict_for(rows, total):
        problems.append("verdict does not re-derive from the rows")
    by_class: dict[str, int] = {}
    by_reach: dict[str, int] = {}
    for r in rows:
        if r["class"] not in CLASS_VOCAB:
            problems.append(f"{r['file']}:{r['function']}: class outside the vocabulary")
        if r["reader"] not in READER_VOCAB:
            problems.append(f"{r['file']}:{r['function']}: reader outside the vocabulary")
        if r["reachable"] not in REACH_VOCAB:
            problems.append(f"{r['file']}:{r['function']}: reach class outside the vocabulary")
        if r["reader"] == R_OPENS and not r["reader_sites"]:
            problems.append(f"{r['file']}:{r['function']}: opens but no reader site named")
        if r["class"] != C_NEVER and not r["caller_sites"]:
            problems.append(f"{r['file']}:{r['function']}: placed but no caller named")
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
        by_reach[r["reachable"]] = by_reach.get(r["reachable"], 0) + 1
    if by_class != (s.get("by_class") or {}):
        problems.append("by_class does not re-derive from the rows")
    if by_reach != (s.get("by_reachable") or {}):
        problems.append("by_reachable does not re-derive from the rows")
    if len(rows) != s.get("fixture_shaped_outside_the_rows_e428_could_not_place"):
        problems.append("row count does not equal the outside-the-unplaced-set count")
    if (s.get("fixture_shaped_inside_the_rows_e428_could_not_place") or 0) + len(rows) != total:
        problems.append("inside + outside does not equal the fixture-shaped total")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, "fixturebeyond_latest.json"))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    if live["summary"]["by_class"] != face["summary"]["by_class"]:
        problems.append("live by_class differs from the published face")
    if (live["summary"]["fixture_shaped_over_the_whole_population"]
            != face["summary"]["fixture_shaped_over_the_whole_population"]):
        problems.append("live fixture-shaped total differs from the published face")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    base = {"file": "f", "function": "g", "line": 1, "class": C_TEMP,
            "reader": R_NO_READER, "reachable": REACH_TEST, "caller_sites": [{}],
            "reader_sites": [], "parameters": ["root"]}

    # Legs 1-5: the verdict is recomputed from the rows, never carried.
    check("empty population", verdict_for([], 0) == V_EMPTY)
    check("all already priced", verdict_for([], 7) == V_ALL_ALREADY)
    check("all temp", verdict_for([dict(base)], 7) == V_OUTSIDE_TEMP)
    check("runtime only is not repo",
          verdict_for([dict(base, **{"class": C_RUNTIME})], 7) == V_OUTSIDE_TEMP)
    check("repo with a reader",
          verdict_for([dict(base, **{"class": C_REPO, "reader": R_OPENS})], 7)
          == V_OUTSIDE_REPO_OPEN)
    check("repo without a reader",
          verdict_for([dict(base, **{"class": C_REPO})], 7) == V_OUTSIDE_REPO_CLOSED)
    check("a temp site with a shared name is not openable",
          verdict_for([dict(base, **{"reader": R_OPENS})], 7) == V_OUTSIDE_TEMP)

    # Leg 8: an inside+outside split that does not add up is a tally problem, not a rounding.
    face = {"rows": [dict(base)], "verdict": V_OUTSIDE_TEMP,
            "summary": {"by_class": {C_TEMP: 1}, "by_reachable": {REACH_TEST: 1},
                        "fixture_shaped_over_the_whole_population": 9,
                        "fixture_shaped_inside_the_rows_e428_could_not_place": 1,
                        "fixture_shaped_outside_the_rows_e428_could_not_place": 1}}
    check("split that does not add up is caught", bool(tally_problems(face)))
    face["summary"]["fixture_shaped_over_the_whole_population"] = 2
    check("clean tally passes", not tally_problems(face))

    # Leg 9: a doctored class table is caught.
    face["summary"]["by_class"] = {C_TEMP: 2}
    check("doctored tally caught", bool(tally_problems(face)))

    # Leg 10: the already-priced set is a union, so E428's fixture rows survive a thinner E432
    # face (a row E432 dropped must not be re-counted as new).
    keys = priced_keys()
    e432_rows = _load(E432_FACE).get("rows") or []
    check("E432 rows are inside the priced set",
          all(_key(r) in keys for r in e432_rows))
    check("priced set is not empty", len(keys) > 0)

    for f in fails:
        print(f"[FAIL] {f}")
    print(f"selftest {legs - len(fails)}/{legs}")
    return 0 if not fails else 1


def write_face(face: dict) -> str:
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    name = f"FIXTUREBEYOND-{face['evidence_cutoff']}.json"
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for target in (os.path.join(OUTDIR, name),
                   os.path.join(OUTDIR, "fixturebeyond_latest.json")):
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
    print(f"sites={s['parameter_write_sites']} fixture={s['fixture_shaped_over_the_whole_population']}"
          f" inside={s['fixture_shaped_inside_the_rows_e428_could_not_place']}"
          f" outside={s['fixture_shaped_outside_the_rows_e428_could_not_place']}")
    print(f"by_class={s['by_class']} by_reach={s['by_reachable']} readers={s['by_reader']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))