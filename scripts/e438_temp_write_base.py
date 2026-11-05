"""E438: of the call rows that hand a callee a temp directory, does the callee write inside it?

E437 published 203 call rows that supply a temp marker for a directory parameter, and priced the
name heuristic against them.  It never asked the second half of the question: a callee that only
*names* the directory -- joins it into a string it returns, or writes to a fixed sibling and merely
takes the directory as an argument -- is counted as a temp writer while it spends no temp file.
That makes the whole temp population an upper bound, and for a shutdown/cleanup question the
difference matters: a directory nobody writes into leaves nothing to clean.

So this study keeps E437's population verbatim (same corpus, same parameter sites, same call-row
unit, same temp label -- imported, never re-implemented) and adds one measurement per call row:
the write paths inside the callee are graded by how they treat the directory parameters.

  * joined    -- the write path composes a name onto a directory parameter
                (os.path.join(p, ...), f"{p}/...", p + "/...", Path(p) / "...")
  * named     -- the write path names the directory parameter but composes nothing onto it
                (it writes the directory path itself, or hands it to something)
  * outside   -- the write path does not name any directory parameter (a fixed sibling, a
                module constant, a second positional argument)

The row is then classed from the set of its callee's writes.  A callee property is a callee
property: rows cluster, so the row share and the distinct-callee share are published side by side
and neither is allowed to stand in for the other.

Scope is stated, not implied: a function that writes nothing at all is not a write site, so it
never entered E437's population either.  The "nowhere" case is therefore invisible here and is
published as an explicit blind spot rather than folded into `outside`.

Usage:
    python scripts/e438_temp_write_base.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from datetime import date

import e429_two_hop_writer as e420
import e432_fixture_write as e432
import e437_name_recall as e437

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST

REACH_PROD = e432.REACH_PROD
REACH_TEST = e432.REACH_TEST

W_JOINED = "composes_a_name_onto_a_directory_parameter"
W_NAMED = "names_a_directory_parameter_without_composing_onto_it"
W_OUTSIDE = "does_not_name_any_directory_parameter"
W_VOCAB = (W_JOINED, W_NAMED, W_OUTSIDE)

C_INSIDE = "every_write_in_the_callee_composes_onto_the_supplied_directory"
C_PARTIAL = "one_write_composes_onto_the_directory_and_one_does_not"
C_NAMES_ONLY = "the_callee_names_the_directory_in_a_write_but_composes_nothing_onto_it"
C_FILE_WRITER = ("the_callee_writes_the_parameter_path_itself_so_its_parameter_is_a_file_path"
                 "_and_the_directory_lands_on_a_file_slot")
C_OUTSIDE = "no_write_in_the_callee_names_the_directory"
C_UNRESOLVED = "the_callee_site_could_not_be_resolved_from_the_scan"
CLASS_VOCAB = (C_INSIDE, C_PARTIAL, C_NAMES_ONLY, C_FILE_WRITER, C_OUTSIDE, C_UNRESOLVED)

V_EMPTY = "no_temp_supplying_call_row_in_the_scan"
V_ALL_SPEND = "every_temp_supplying_call_row_reaches_a_callee_that_writes_inside_the_directory"
V_SOME = ("some_temp_supplying_call_rows_reach_a_callee_that_never_writes_inside_the_supplied"
          "_directory")
VERDICT_VOCAB = (V_EMPTY, V_ALL_SPEND, V_SOME)

POPULATION_KEYS = ("corpus_sources", "directory_parameter_call_rows", "temp_supplying_call_rows")

_NAME_TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def names_param(text: str, param: str) -> bool:
    """Does this write-path text use the parameter as a name (not as a substring of another)?"""
    if not text or not param:
        return False
    return any(tok == param for tok in _NAME_TOK.findall(text))


def joins_param(text: str, param: str) -> bool:
    """Does the write path compose something onto the parameter?

    Four spellings, all of them the ones this corpus actually uses.  A bare ``open(p)`` is
    deliberately *not* a join: writing the directory path itself is the W_NAMED case and the
    distinction is the whole point of the study.
    """
    if not names_param(text, param):
        return False
    p = re.escape(param)
    patterns = (
        r"os\.path\.join\(\s*(?:str\(\s*)?%s\s*[,)]" % p,
        r"\bPath\(\s*%s\s*\)\s*/" % p,
        r"\b%s\s*/\s*" % p,
        r"\b%s\s*\+\s*" % p,
        r"f['\"][^'\"]*\{\s*%s\s*\}" % p,
    )
    return any(re.search(pat, text) for pat in patterns)


def write_kind(text: str, params: list[str]) -> str:
    named = [p for p in params if names_param(text, p)]
    if not named:
        return W_OUTSIDE
    if any(joins_param(text, p) for p in named):
        return W_JOINED
    return W_NAMED


def class_of(kinds: list[str]) -> str:
    if not kinds:
        return C_UNRESOLVED
    joined = [k for k in kinds if k == W_JOINED]
    outside = [k for k in kinds if k == W_OUTSIDE]
    named = [k for k in kinds if k == W_NAMED]
    if joined and not outside and not named:
        return C_INSIDE
    if joined and (outside or named):
        return C_PARTIAL
    if named:
        return C_NAMES_ONLY
    return C_OUTSIDE


def verdict_for(rows: list[dict]) -> str:
    """Recomputed from the published rows, never carried."""
    if not rows:
        return V_EMPTY
    inside = sum(1 for r in rows if r["write_class"] == C_INSIDE)
    if inside == len(rows):
        return V_ALL_SPEND
    return V_SOME


def build(cutoff: str | None = None) -> dict:
    cut = cutoff or _load(e437.E434_FACE)["evidence_cutoff"]
    sources = [p for p in e437.corpus()
               if not os.path.basename(p).startswith(("e438", "_e438", "run_e438"))]
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print(f"stage: {len(param)} parameter sites over {len(sources)} sources", flush=True)
    rows_all = e437.call_rows(param, index)
    temp_rows = [r for r in rows_all if e437.is_temp_call(r["argument"])]
    print(f"stage: {len(temp_rows)} temp-supplying call rows of {len(rows_all)}", flush=True)

    by_key = {(s.path, s.func, s.line): s for s in param}
    published: list[dict] = []
    for r in temp_rows:
        site = by_key.get((r["callee_file"], r["callee_function"], r["callee_line"]))
        params = site.parameter_directories() if site is not None else []
        writes = []
        for text, _node in (site.paths if site else []):
            kind = write_kind(text, params)
            shown = text
            if kind == W_OUTSIDE:
                # a write through a local name (`hp = os.path.join(root, ...)`) names no
                # parameter in its own text; resolve it through the function's own bindings
                # before calling it outside, or the instrument would grade a path it can see
                resolved = e420.resolve(text, site.envs) if site is not None else text
                kind2 = write_kind(resolved, params)
                if kind2 != W_OUTSIDE:
                    kind = kind2
                    shown = f"{text} -> {resolved}"
            writes.append((shown, kind, text if shown == text else shown.split(" -> ", 1)[1]))
        cls = class_of([k for _t, k, _e in writes])
        if cls == C_NAMES_ONLY and params and all(
                _e.strip() in params for _t, k, _e in writes if k == W_NAMED):
            # every naming write is the parameter path itself: the callee is a file-path writer
            # and the caller handed a directory to a slot that wants a file
            cls = C_FILE_WRITER
        published.append({
            "callee_file": r["callee_file"],
            "callee_function": r["callee_function"],
            "callee_line": r["callee_line"],
            "caller_file": r["caller_file"],
            "caller_function": r["caller_function"],
            "caller_line": r["caller_line"],
            "argument": r["argument"][:200],
            "caller_kind": e437.caller_kind({"file": r["caller_file"],
                                             "caller": r["caller_function"]}),
            "write_class": cls,
            "directory_parameters": params,
            "write_kinds": [k for _t, k, _e in writes],
            "write_paths": [t[:200] for t, _k, _e in writes][:6],
        })
    published.sort(key=lambda r: (r["write_class"], r["callee_file"] or "",
                                  r["callee_line"] or 0, r["caller_line"] or 0))

    tally = {c: 0 for c in CLASS_VOCAB}
    for r in published:
        tally[r["write_class"]] = tally.get(r["write_class"], 0) + 1
    by_callee: dict[str, str] = {}
    for r in published:
        by_callee[r["callee_function"]] = r["write_class"]
    callee_tally = {c: 0 for c in CLASS_VOCAB}
    for cls in by_callee.values():
        callee_tally[cls] = callee_tally.get(cls, 0) + 1
    rows_by_kind: dict[str, int] = {}
    for r in published:
        rows_by_kind[r["caller_kind"]] = rows_by_kind.get(r["caller_kind"], 0) + 1
    non_spending = [r for r in published if r["write_class"] != C_INSIDE]
    summary = {
        "corpus_sources": len(sources),
        "parameter_write_sites": len(param),
        "directory_parameter_call_rows": len(rows_all),
        "temp_supplying_call_rows": len(published),
        "rows_by_write_class": tally,
        "distinct_callees": len(by_callee),
        "callees_by_write_class": callee_tally,
        "rows_by_caller_kind": rows_by_kind,
        "rows_that_really_spend_the_directory": tally.get(C_INSIDE, 0),
        "share_of_rows_that_really_spend_it": (round(tally.get(C_INSIDE, 0) / len(published), 4)
                                               if published else None),
        "upper_bound_shrink": {
            "as_published_by_E437": len(published),
            "after_grading": tally.get(C_INSIDE, 0),
            "overstatement": len(non_spending),
        },
        "non_spending_callees": sorted(
            {(r["callee_function"], r["write_class"]) for r in non_spending})[:15],
        "directory_passed_to_a_file_path_parameter": {
            "call_rows": tally.get(C_FILE_WRITER, 0),
            "distinct_callees": callee_tally.get(C_FILE_WRITER, 0),
            "callees": sorted({(r["callee_file"], r["callee_function"])
                               for r in published if r["write_class"] == C_FILE_WRITER}),
            "reading": "these call rows hand a directory to a callee whose only write is the "
                       "parameter path itself (json.dump/save/write_json wrappers); the "
                       "directory lands on a file slot, so nothing is written inside it and the "
                       "call would fail if it ever ran against the real path",
        },
        "non_spending_examples": [
            {"callee": r["callee_function"], "class": r["write_class"],
             "caller_file": r["caller_file"], "caller_line": r["caller_line"],
             "writes": r["write_paths"][:2], "parameters": r["directory_parameters"]}
            for r in non_spending[:10]
        ],
    }
    return {
        "study": "E438_which_temp_supplying_call_row_spends_a_directory_the_callee_never_writes",
        "card": "E438-WHICH-PASSER-SPENDS-A-TEMP-DIRECTORY-THE-CALLEE-NEVER-WRITES",
        "title": "grade every temp-supplying directory-parameter call row by whether the callee's "
                 "write paths compose a name onto the supplied directory",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(published),
        "class_vocab": list(CLASS_VOCAB),
        "write_kind_vocab": list(W_VOCAB),
        "population_keys": list(POPULATION_KEYS),
        "summary": summary,
        "rows": published,
        "method_limits": [
            "the population is E437's, imported rather than re-derived: same corpus, same "
            "parameter sites, same call-row unit, same temp marker text; a disagreement between "
            "this face and namerecall_latest.json is a defect in this file, not a new measurement",
            "write paths are the ones the scan already classified as path writes (open for "
            "writing, write_text/write_bytes, the pandas/image save family); a write performed by "
            "a callee this function calls is not followed, so C_INSIDE means 'this function "
            "spells a path inside the directory', not 'the bytes definitely land there'",
            "a function that writes nothing is not a write site and never enters the population, "
            "so the 'composes a name and someone else writes it' case is outside this scan -- it "
            "is published as a blind spot and is NOT counted in C_OUTSIDE",
            "join detection covers four spellings (os.path.join, Path(p)/x, p + '/x', f'{p}/x'); "
            "a path built by a helper that takes the directory as an argument reads as W_NAMED, "
            "which is reported as its own class rather than folded into inside or outside",
            "a callee with several directory parameters is graded over all of them, so a write "
            "that composes onto parameter B is counted as inside even when the row supplied A",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "tempwritebase_latest.json")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
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
    tally = {c: 0 for c in CLASS_VOCAB}
    for r in rows:
        if r.get("write_class") not in CLASS_VOCAB:
            problems.append("%s:%s write class outside the vocabulary"
                            % (r.get("caller_file"), r.get("caller_line")))
            continue
        tally[r["write_class"]] += 1
        kinds = r.get("write_kinds") or []
        if r["write_class"] == C_INSIDE and any(k != W_JOINED for k in kinds):
            problems.append("%s:%s claimed inside with a non-joining write"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r["write_class"] == C_OUTSIDE and any(k != W_OUTSIDE for k in kinds):
            problems.append("%s:%s claimed outside with a naming write"
                            % (r.get("caller_file"), r.get("caller_line")))
        if r["write_class"] != C_UNRESOLVED and not kinds:
            problems.append("%s:%s classed without any write path"
                            % (r.get("caller_file"), r.get("caller_line")))
        for text in r.get("write_paths") or []:
            if not (text or "").strip():
                problems.append("%s:%s carries an empty write path"
                                % (r.get("caller_file"), r.get("caller_line")))
    if tally != (s.get("rows_by_write_class") or {}):
        problems.append("rows_by_write_class does not re-derive from the rows")
    if sum(tally.values()) != s.get("temp_supplying_call_rows"):
        problems.append("the class tally does not add up to the temp-supplying rows")
    if tally.get(C_INSIDE, 0) != s.get("rows_that_really_spend_the_directory"):
        problems.append("rows_that_really_spend_the_directory does not re-derive")
    if s.get("temp_supplying_call_rows") and s.get("share_of_rows_that_really_spend_it") is not None:
        want = round(tally.get(C_INSIDE, 0) / s["temp_supplying_call_rows"], 4)
        if abs(want - s["share_of_rows_that_really_spend_it"]) > 1e-9:
            problems.append("the published share does not re-derive")
    shrink = s.get("upper_bound_shrink") or {}
    if shrink.get("as_published_by_E437") != s.get("temp_supplying_call_rows"):
        problems.append("upper_bound_shrink does not start from the temp rows")
    if shrink.get("after_grading") != tally.get(C_INSIDE, 0):
        problems.append("upper_bound_shrink does not end at the inside rows")
    if shrink.get("overstatement") != sum(v for k, v in tally.items() if k != C_INSIDE):
        problems.append("upper_bound_shrink overstatement does not re-derive")
    by_callee = {r.get("callee_function"): r.get("write_class") for r in rows}
    callee_tally = {c: 0 for c in CLASS_VOCAB}
    for cls in by_callee.values():
        if cls in callee_tally:
            callee_tally[cls] += 1
    if callee_tally != (s.get("callees_by_write_class") or {}):
        problems.append("callees_by_write_class does not re-derive from the rows")
    if len(by_callee) != s.get("distinct_callees"):
        problems.append("distinct_callees does not re-derive from the rows")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, "tempwritebase_latest.json"))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    if live["summary"]["rows_by_write_class"] != face["summary"]["rows_by_write_class"]:
        problems.append("live class tally differs from the published face")
    if (live["summary"]["temp_supplying_call_rows"]
            != face["summary"]["temp_supplying_call_rows"]):
        problems.append("live temp row count differs from the published face")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    check("join_ospath", joins_param('os.path.join(d, "x.csv")', "d"))
    check("join_path_slash", joins_param('Path(d) / "x.csv"', "d"))
    check("join_plus", joins_param('d + "/x.csv"', "d"))
    check("join_fstring", joins_param('f"{d}/x.csv"', "d"))
    check("join_str_wrapped", joins_param('os.path.join(str(d), "x")', "d"))
    check("bare_dir_is_not_a_join", not joins_param("open(d, 'w')", "d"))
    check("other_name_is_not_named", not names_param("open(day_dir, 'w')", "d"))
    check("substring_is_not_named", not names_param('os.path.join(dx, "a")', "d"))

    check("class_all_joined", class_of([W_JOINED, W_JOINED]) == C_INSIDE)
    check("class_mixed", class_of([W_JOINED, W_OUTSIDE]) == C_PARTIAL)
    check("class_named_only", class_of([W_NAMED]) == C_NAMES_ONLY)
    check("class_outside", class_of([W_OUTSIDE, W_OUTSIDE]) == C_OUTSIDE)
    check("class_unresolved", class_of([]) == C_UNRESOLVED)
    check("write_kind_outside", write_kind('open("data/x.csv", "w")', ["d"]) == W_OUTSIDE)
    check("write_kind_named", write_kind("open(d, 'w')", ["d"]) == W_NAMED)
    check("write_kind_joined",
          write_kind('os.path.join(d, "x")', ["d"]) == W_JOINED)

    inside = {"callee_function": "a", "write_class": C_INSIDE, "caller_kind": REACH_PROD,
              "caller_file": "scripts/x.py", "caller_line": 1,
              "write_kinds": [W_JOINED], "write_paths": ["os.path.join(d, 'x')"],
              "callee_file": "scripts/y.py", "callee_line": 1,
              "callee_function_dup": None, "directory_parameters": ["d"]}
    inside.pop("callee_function_dup")
    outside = dict(inside, callee_function="b", write_class=C_NAMES_ONLY,
                   write_kinds=[W_NAMED], write_paths=["open(d, 'w')"])
    check("verdict_all", verdict_for([inside]) == V_ALL_SPEND)
    check("verdict_some", verdict_for([inside, outside]) == V_SOME)
    check("verdict_empty", verdict_for([]) == V_EMPTY)

    face = {"verdict": V_SOME, "rows": [inside, outside],
            "summary": {
                "rows_by_write_class": {c: 0 for c in CLASS_VOCAB},
                "temp_supplying_call_rows": 2,
                "rows_that_really_spend_the_directory": 1,
                "share_of_rows_that_really_spend_it": 0.5,
                "upper_bound_shrink": {"as_published_by_E437": 2, "after_grading": 1,
                                       "overstatement": 1},
                "distinct_callees": 2,
                "callees_by_write_class": {c: 0 for c in CLASS_VOCAB},
            }}
    face["summary"]["rows_by_write_class"][C_INSIDE] = 1
    face["summary"]["rows_by_write_class"][C_NAMES_ONLY] = 1
    face["summary"]["callees_by_write_class"][C_INSIDE] = 1
    face["summary"]["callees_by_write_class"][C_NAMES_ONLY] = 1
    check("tally_clean", tally_problems(face) == [])
    bad = json.loads(json.dumps(face))
    bad["summary"]["rows_by_write_class"][C_INSIDE] = 0
    check("tally_catches_a_shifted_cell", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(face))
    bad2["rows"][0]["write_class"] = C_INSIDE
    bad2["rows"][0]["write_kinds"] = [W_OUTSIDE]
    check("tally_catches_inside_without_a_join", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(face))
    bad3["verdict"] = V_ALL_SPEND
    check("tally_catches_a_carried_verdict", tally_problems(bad3) != [])

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
        print(json.dumps(face["summary"]["rows_by_write_class"], ensure_ascii=False))
        print(f"share of temp rows that really spend the directory: "
              f"{face['summary']['share_of_rows_that_really_spend_it']}")
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