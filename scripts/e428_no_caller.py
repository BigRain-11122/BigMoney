"""E428: price the 35 parameter-directory write sites E420 could not place.

E420 followed 310 write sites whose persisted path is composed with a directory that arrives
as a function parameter, and offered each of them to a call index built from the corpus.  254
received a literal directory from a caller, 21 received a constant, and 35 were published as
``no_caller_found_in_the_corpus``.

That 35 was never a statement about the corpus.  E420 built its call index only from the
helper names that occur on a *non-literal* parameter site (``wanted`` in its build step), so a
helper that is also used somewhere with a literal directory -- ``_mk_fixture`` and
``write_fixture`` are the obvious ones -- was never indexed at all.  A site whose callee is
missing from the index reads exactly like a site whose callee is missing from the corpus.

This study separates the two.  It rebuilds the same index over *every* parameter-directory
helper name (97 instead of 75) and re-grades the same 310 sites, then classifies each of the
original 35 by what the wider index says:

  * ``unplaced_only_because_the_helper_was_not_in_the_call_index`` -- the callee is called in
    the corpus, with an argument that resolves for this parameter, and the narrow index simply
    never looked.  This class is a defect of the instrument, not of the tree.
  * ``call_sites_exist_but_never_supply_the_parameter`` -- calls exist, but no call passes a
    directory for this parameter (a ``write=None`` default is the canonical shape: the site
    writes only when a caller opts in).
  * ``no_call_site_anywhere`` -- nothing in the python corpus calls it.
  * ``named_only_outside_the_python_corpus`` -- no python call, but a Tools/*.ps1, a doc or a
    subprocess argv string names the helper, so it is reachable and must not be called dead.

The class order is deliberate: a site is only ``no_call_site_anywhere`` when no python call and
no non-python mention exists, because calling a write site dead is a claim about the world, not
about the census.

Usage:
    python scripts/e428_no_caller.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import date

import e429_two_hop_writer as e420

ROOT = e420.ROOT
ST = e420.ST
E420_FACE = os.path.join(ST, "twohop_latest.json")
OUTDIR = ST

C_NARROW_ONLY = "unplaced_only_because_the_helper_was_not_in_the_call_index"
C_DEFAULT_ONLY = "call_sites_exist_but_never_supply_the_parameter"
C_NOT_CALLED = "no_call_site_anywhere"
C_OUTSIDE = "named_only_outside_the_python_corpus"
CLASS_VOCAB = (C_NARROW_ONLY, C_DEFAULT_ONLY, C_NOT_CALLED, C_OUTSIDE)

V_ALL_INDEX = "every_unplaced_site_is_placed_once_the_index_covers_every_parameter_helper"
V_MOST_INDEX = "most_unplaced_sites_are_unplaced_by_the_index_and_not_by_the_corpus"
V_FEW_INDEX = "most_unplaced_sites_are_unplaced_by_the_corpus_even_with_the_wider_index"
V_EMPTY = "no_unplaced_site_to_place"
VERDICT_VOCAB = (V_ALL_INDEX, V_MOST_INDEX, V_FEW_INDEX, V_EMPTY)

# Counts that move when a .py file appears or is deleted.  Declared, never equality-gated by
# the leg (scripts/population_keys.py, r1441 law).
POPULATION_KEYS = ("corpus_sources", "parameter_write_sites")

# Where a helper name can be named without being a cut scan of the whole disk.
MENTION_EXTS = {".ps1", ".cmd", ".bat", ".md", ".txt", ".json", ".yml", ".yaml", ".toml",
                ".cfg"}
MENTION_PRUNE = {".git", "data", "results", "__pycache__", "legacy", "Money02", ".codely-cli"}
MENTION_MAX_BYTES = 300 * 1024
FIXTURE_HINT = e420.e419.FIXTURE_HINT
FIXTURE_WORDS = ("fixture", "_mk", "_stub", "_toy", "write_fixture", "_panel", "_save")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list[str]:
    """E419/E420's scope, minus this study's own files (self-inclusion law, E180/E207)."""
    return [p for p in e420.corpus()
            if not os.path.basename(p).startswith(("e428", "_e428", "run_e428"))]


# ---------------------------------------------------------------- the two instruments

def supplied_arguments(site, index: dict[str, list[dict]]) -> list[str]:
    """Every text a call site passes for one of this site's directory parameters."""
    out: list[str] = []
    rows = index.get(site.func) or []
    for param in site.parameter_directories():
        for row in rows:
            arg = e420.resolve_call_argument(row, param, site.params)
            if arg:
                out.append(arg)
    return out


def grade(site, index: dict[str, list[dict]]) -> str:
    """literal / constant / none, exactly the three states E420 publishes."""
    supplied = supplied_arguments(site, index)
    if not supplied:
        return "none"
    if any('"' in a or "'" in a for a in supplied):
        return "literal"
    return "constant"


# ---------------------------------------------------------------- mentions outside the census

def mention_scan(names: set[str]) -> dict[str, dict[str, list[str]]]:
    """Where each name is spelled outside the python corpus, and which python files name it.

    Chat transcripts under ``.codely-cli/auto-saves`` are pruned: a transcript quoting a helper
    is not a caller, and the first draft counted one as a non-python reach point.
    """
    out = {n: {"non_python": [], "python": []} for n in names}
    if not names:
        return out
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in MENTION_PRUNE]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if fn.startswith(("e428", "_e428", "run_e428")):
                continue
            is_py = ext == ".py"
            if not is_py and ext not in MENTION_EXTS:
                continue
            path = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(path) > MENTION_MAX_BYTES:
                    continue
                text = io.open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            rel = _rel(path)
            for name in names:
                if name in text:
                    out[name]["python" if is_py else "non_python"].append(rel)
    for name, hits in out.items():
        for key in ("python", "non_python"):
            hits[key].sort()
            hits[key] = hits[key][:12]
    return out


def call_sites_of(name: str, index: dict[str, list[dict]]) -> list[dict]:
    return [{"file": r["file"], "caller": r["caller"], "line": r["line"],
             "args": r["args"][:3]}
            for r in (index.get(name) or [])[:8]]


# ---------------------------------------------------------------- classification

def reason_class(site, index_wide: dict[str, list[dict]], mentions: dict) -> str:
    """One of CLASS_VOCAB, in the order declared in the module docstring."""
    if supplied_arguments(site, index_wide):
        return C_NARROW_ONLY
    if index_wide.get(site.func):
        return C_DEFAULT_ONLY
    hits = mentions.get(site.func) or {"non_python": [], "python": []}
    if hits["non_python"]:
        return C_OUTSIDE
    return C_NOT_CALLED


def verdict_for(rows: list[dict]) -> str:
    if not rows:
        return V_EMPTY
    narrow_only = sum(1 for r in rows if r["class"] == C_NARROW_ONLY)
    if narrow_only == len(rows):
        return V_ALL_INDEX
    if narrow_only * 2 > len(rows):
        return V_MOST_INDEX
    return V_FEW_INDEX


def _fixture_shaped(site) -> bool:
    hay = " ".join([site.func, site.path]).lower()
    return any(w in hay for w in FIXTURE_WORDS)


# ---------------------------------------------------------------- build

def build(cutoff: str | None = None) -> dict:
    e420_face = _load(E420_FACE)
    cut = cutoff or e420_face["evidence_cutoff"]
    sources = corpus()
    sites, parsed = e420.scan_corpus(sources)
    param_sites = [s for found in sites.values() for s in found if s.parameter_directories()]

    narrow_names = {s.func for s in param_sites if not s.spells_a_literal()}
    wide_names = {s.func for s in param_sites}
    index_wide = e420.main_call_index(wide_names, sources)
    index_narrow = {n: index_wide.get(n) or [] for n in narrow_names}

    # The producer's instrument, reproduced: it is the narrow index that published 35.
    unplaced = [s for s in param_sites if grade(s, index_narrow) == "none"]
    mentions = mention_scan({s.func for s in unplaced} | {s.func for s in
                                                           [x for x in param_sites
                                                            if grade(x, index_wide) == "none"]})

    rows: list[dict] = []
    for s in unplaced:
        cls = reason_class(s, index_wide, mentions)
        hits = mentions.get(s.func) or {"non_python": [], "python": []}
        rows.append({
            "file": s.path,
            "function": s.func,
            "line": s.line,
            "write_call": s.call_name,
            "parameters": s.parameter_directories(),
            "literal_in_the_site_path": s.spells_a_literal(),
            "calls_in_the_narrow_index": len(index_narrow.get(s.func) or []),
            "calls_in_the_wide_index": len(index_wide.get(s.func) or []),
            "call_sites": call_sites_of(s.func, index_wide),
            "non_python_mentions": hits["non_python"],
            "python_files_naming_it": [p for p in hits["python"] if p != s.path][:6],
            "fixture_shaped": _fixture_shaped(s),
            "class": cls,
        })
    rows.sort(key=lambda r: (r["class"], r["file"], r["line"]))

    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1

    wide_none = [s for s in param_sites if grade(s, index_wide) == "none"]
    re_derived = {
        "parameter_derived_sites": len(param_sites),
        "caller_supplies_a_literal_directory": sum(
            1 for s in param_sites if grade(s, index_wide) == "literal"),
        "caller_supplies_a_constant_directory": sum(
            1 for s in param_sites if grade(s, index_wide) == "constant"),
        "no_caller_found_in_the_corpus": len(wide_none),
        "helper_names_resolved": len(wide_names),
    }
    published = (e420_face.get("summary") or {}).get("two_hop_reach") or {}

    summary = {
        "parameter_write_sites": len(param_sites),
        "unplaced_under_the_producer_instrument": len(unplaced),
        "unplaced_after_the_index_covers_every_parameter_helper": len(wide_none),
        "by_class": by_class,
        "fixture_shaped_sites": sum(1 for r in rows if r["fixture_shaped"]),
        "helper_names_narrow": len(narrow_names),
        "helper_names_wide": len(wide_names),
        "helper_names_never_indexed_by_the_producer": len(wide_names - narrow_names),
        "corpus_sources": parsed,
        "population": {"narrow_index": len(unplaced), "wide_index": len(wide_none)},
    }
    return {
        "study": "E428_which_parameter_directory_helper_has_no_caller_in_the_census",
        "card": "E428-WHICH-PARAMETER-DIRECTORY-HELPER-HAS-NO-CALLER-IN-THE-CENSUS",
        "title": "price the 35 parameter-directory write sites the E420 call index could not "
                 "place, splitting the instrument's blind spot from the tree's silence",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(rows),
        "class_vocab": list(CLASS_VOCAB),
        "population_keys": list(POPULATION_KEYS),
        "summary": summary,
        "correction": {
            "face": "results/state_tilt/twohop_latest.json",
            "block": "summary.two_hop_reach",
            "published_by_e420": published,
            "re_derived_with_the_wide_index": re_derived,
            "note": "E420's own three face rows are untouched by this study; only its corpus "
                    "half moves, because the call index it offered them to was built from "
                    "non-literal parameter helper names only",
        },
        "rows": rows,
        "method_limits": [
            "the wide index is still name-based: a helper name shared by two files admits a "
            "foreign call site, so a hit is a place the directory could come from, not proof "
            "of which call produced the face on disk",
            "the mention scan covers text extensions under 300 KB and prunes data/, results/, "
            "legacy/, Money02/ and .codely-cli/; a helper named only in a file it skipped "
            "reads as no_call_site_anywhere",
            "fixture_shaped is a name heuristic (func or path contains fixture/_mk/_toy/"
            "_stub/_panel/_save), not a measurement of whether the code is a test",
            "no writer was edited and no face on disk was read: this is a census of source "
            "text, so a site deleted in the tree since the last scan is invisible",
        ],
    }


# ---------------------------------------------------------------- gates

def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face["rows"]
    s = face["summary"]
    if face["verdict"] not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    if face["verdict"] != verdict_for(rows):
        problems.append("verdict does not re-derive from the rows")
    for r in rows:
        if r["class"] not in CLASS_VOCAB:
            problems.append(f"{r['file']}:{r['function']}: class outside the vocabulary")
        if r["class"] == C_NARROW_ONLY and not r["call_sites"]:
            problems.append(f"{r['file']}:{r['function']}: index-blind but no call site named")
        if r["class"] == C_OUTSIDE and not r["non_python_mentions"]:
            problems.append(f"{r['file']}:{r['function']}: outside-only but nothing names it")
        if r["class"] == C_NOT_CALLED and r["call_sites"]:
            problems.append(f"{r['file']}:{r['function']}: called but graded silent")
    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    if by_class != (s.get("by_class") or {}):
        problems.append("by_class does not re-derive from the rows")
    if sum(by_class.values()) != s.get("unplaced_under_the_producer_instrument"):
        problems.append("row count does not equal unplaced_under_the_producer_instrument")
    if s.get("unplaced_under_the_producer_instrument") != len(rows):
        problems.append("summary unplaced count differs from the row count")
    if s.get("fixture_shaped_sites") != sum(1 for r in rows if r["fixture_shaped"]):
        problems.append("fixture_shaped_sites does not re-derive")
    if s.get("helper_names_never_indexed_by_the_producer") != (
            (s.get("helper_names_wide") or 0) - (s.get("helper_names_narrow") or 0)):
        problems.append("never-indexed helper count does not re-derive")
    corr = face["correction"]["re_derived_with_the_wide_index"]
    if sum(v for k, v in corr.items() if k != "parameter_derived_sites"
           and k != "helper_names_resolved") != corr["parameter_derived_sites"]:
        problems.append("re-derived three states do not sum to the parameter sites")
    if corr["no_caller_found_in_the_corpus"] != s.get(
            "unplaced_after_the_index_covers_every_parameter_helper"):
        problems.append("re-derived no-caller count differs from the summary")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, "no_caller_latest.json"))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"verdict moved on re-derivation: {face['verdict']} -> "
                        f"{live['verdict']}")
    for key in ("unplaced_under_the_producer_instrument",
                "unplaced_after_the_index_covers_every_parameter_helper",
                "by_class", "fixture_shaped_sites"):
        if live["summary"][key] != face["summary"][key]:
            problems.append(f"{key} moved: {face['summary'][key]} -> {live['summary'][key]}")
    live_rows = {(r["file"], r["function"], r["line"]): r["class"] for r in live["rows"]}
    face_rows = {(r["file"], r["function"], r["line"]): r["class"] for r in face["rows"]}
    for key, cls in face_rows.items():
        if key not in live_rows:
            problems.append(f"{key[0]}:{key[1]}: row gone from the live build")
        elif live_rows[key] != cls:
            problems.append(f"{key[0]}:{key[1]}: class moved {cls} -> {live_rows[key]}")
    if face["correction"]["re_derived_with_the_wide_index"] != live["correction"][
            "re_derived_with_the_wide_index"]:
        problems.append("re-derived corpus block moved")
    return problems


def selftest() -> int:
    """Offline: the classifier, the verdict, and the tally, on synthetic sites."""
    class FakeSite:
        def __init__(self, func, path, params, names, literal=False):
            self.func = func
            self.path = path
            self.params = params
            self._names = names
            self._literal = literal
            self.line = 1
            self.call_name = "open"

        def names_in_path(self):
            return set(self._names)

        def parameter_directories(self):
            return [p for p in self.params if p in self._names]

        def spells_a_literal(self):
            return self._literal

        def segment(self):
            return ""

    cases = []
    idx = {"h_hit": [{"file": "a.py", "caller": "f", "line": 3, "args": ['"d"'],
                      "kwargs": {}, "env": {}}]}
    s1 = FakeSite("h_hit", "a.py", ["outdir"], ["outdir"])
    cases.append(("narrow only", reason_class(s1, idx, {}), C_NARROW_ONLY))
    s2 = FakeSite("h_default", "b.py", ["elig", "grids", "write"], ["write"])
    idx["h_default"] = [{"file": "b.py", "caller": "f", "line": 9, "args": ["a", "b"],
                         "kwargs": {}, "env": {}}]
    cases.append(("default only", reason_class(s2, idx, {}), C_DEFAULT_ONLY))
    s3 = FakeSite("h_silent", "c.py", ["out_json"], ["out_json"])
    cases.append(("silent", reason_class(s3, idx, {}), C_NOT_CALLED))
    cases.append(("outside", reason_class(s3, idx, {"h_silent": {
        "non_python": ["Tools/x.ps1"], "python": []}}), C_OUTSIDE))
    # a name that is only ever named in python but never called is still silent: the class is
    # about reach, and a python file naming a helper it does not call is not a caller
    cases.append(("python mention only", reason_class(s3, idx, {"h_silent": {
        "non_python": [], "python": ["d.py"]}}), C_NOT_CALLED))

    ok = 0
    for name, got, want in cases:
        if got == want:
            ok += 1
        else:
            print(f"selftest FAIL {name}: {got} != {want}")

    vcases = [
        ([], V_EMPTY),
        ([{"class": C_NARROW_ONLY}, {"class": C_NARROW_ONLY}], V_ALL_INDEX),
        ([{"class": C_NARROW_ONLY}, {"class": C_NOT_CALLED}, {"class": C_NOT_CALLED}],
         V_FEW_INDEX),
        ([{"class": C_NARROW_ONLY}, {"class": C_NARROW_ONLY}, {"class": C_NOT_CALLED}],
         V_MOST_INDEX),
    ]
    for rows, want in vcases:
        if verdict_for(rows) == want:
            ok += 1
        else:
            print(f"selftest FAIL verdict: {verdict_for(rows)} != {want}")

    # tally catches a doctored count and a class outside the vocabulary
    face = {
        "verdict": V_FEW_INDEX,
        "summary": {"by_class": {C_NARROW_ONLY: 1, C_NOT_CALLED: 1},
                    "unplaced_under_the_producer_instrument": 2,
                    "unplaced_after_the_index_covers_every_parameter_helper": 2,
                    "fixture_shaped_sites": 1, "helper_names_narrow": 75,
                    "helper_names_wide": 97, "helper_names_never_indexed_by_the_producer": 22},
        "rows": [{"file": "a.py", "function": "f", "line": 1, "class": C_NARROW_ONLY,
                  "call_sites": [{"file": "a.py"}], "non_python_mentions": [],
                  "fixture_shaped": True},
                 {"file": "b.py", "function": "g", "line": 1, "class": C_NOT_CALLED,
                  "call_sites": [], "non_python_mentions": [],
                  "fixture_shaped": False}],
        "correction": {"re_derived_with_the_wide_index": {
            "parameter_derived_sites": 310, "caller_supplies_a_literal_directory": 286,
            "caller_supplies_a_constant_directory": 22, "no_caller_found_in_the_corpus": 2,
            "helper_names_resolved": 97}},
    }
    if tally_problems(face):
        print(f"selftest FAIL clean fixture raised: {tally_problems(face)}")
    else:
        ok += 1
    bad = json.loads(json.dumps(face))
    bad["rows"][0]["class"] = "made_up"
    if tally_problems(bad):
        ok += 1
    else:
        print("selftest FAIL doctored class not caught")
    bad2 = json.loads(json.dumps(face))
    bad2["summary"]["by_class"] = {C_NARROW_ONLY: 3}
    if tally_problems(bad2):
        ok += 1
    else:
        print("selftest FAIL doctored by_class not caught")
    bad3 = json.loads(json.dumps(face))
    bad3["correction"]["re_derived_with_the_wide_index"]["caller_supplies_a_literal_directory"] = 288
    if tally_problems(bad3):
        ok += 1
    else:
        print("selftest FAIL doctored sum not caught")

    total = len(cases) + len(vcases) + 4
    print(f"selftest {ok}/{total}")
    return 0 if ok == total else 1


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        problems = verify()
    elif mode == "run":
        face = build()
        problems = tally_problems(face)
        if not problems:
            os.makedirs(OUTDIR, exist_ok=True)
            cut = face["evidence_cutoff"].replace("-", "")
            with io.open(os.path.join(OUTDIR, f"NO_CALLER-{face['evidence_cutoff']}.json"),
                         "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            with io.open(os.path.join(OUTDIR, "no_caller_latest.json"), "w",
                         encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            print(json.dumps({"verdict": face["verdict"], "summary": face["summary"],
                              "correction": face["correction"]["re_derived_with_the_wide_index"],
                              "cut": cut}, ensure_ascii=False, indent=1))
    else:
        print(__doc__)
        return 2
    if problems:
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 1
    print("problems=[]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))