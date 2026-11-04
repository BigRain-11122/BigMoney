"""E432: price the 21 fixture-shaped parameter-directory write sites E428 counted and left alone.

E428 counted 21 of its 35 unplaced rows as ``fixture_shaped`` by a name heuristic (function or
path contains fixture/_mk/_toy/_stub/_panel/_save) and published the count without asking a
single question about what those sites actually write.  A name is not a measurement: a function
called ``_mk_fixture`` may write into ``tempfile.mkdtemp()``, into a literal ``results/`` path,
or into a directory its caller forwards from a module constant.

This study resolves, for each of those 21 sites, the directory its callers actually pass, and
then asks the two questions that decision a fixture writer needs:

  * **where does it land** -- ``temp`` (a temporary directory constructor appears in the
    argument the caller supplies), ``repo_relative`` (the caller spells a quoted path inside the
    tree), ``runtime_constant`` (an unquoted name: a module constant, a forwarded parameter, a
    computed path), or ``never_supplied`` (calls exist but none fills this parameter -- a
    ``write=None`` default, so the site writes only when a caller opts in).
  * **can a reader in this corpus open what it writes** -- the composed file name is matched
    against the arguments of read calls in the corpus.  A temp-directory write is unreachable
    on disk but still executes; the study therefore separates *unreachable on disk* from *not
    called at all* and refuses to call any of the 21 dead.

Population premise correction (published, not silently repaired): E428's card in the pool says
"21 of its 310"; the 21 are in fact a subset of the 35 *unplaced* rows, i.e. the sites whose
caller E428 could not name under its narrow index.  The rows are read from the published face
and re-graded against a live index, never hand-copied.

Usage:
    python scripts/e432_fixture_write.py run|verify|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

import e428_no_caller as e428
import e429_two_hop_writer as e420

ROOT = e420.ROOT
ST = e420.ST
E428_FACE = os.path.join(ST, "no_caller_latest.json")
OUTDIR = ST

C_TEMP = "temp"
C_REPO = "repo_relative"
C_RUNTIME = "runtime_constant"
C_NEVER = "never_supplied"
CLASS_VOCAB = (C_TEMP, C_REPO, C_RUNTIME, C_NEVER)

R_OPENS = "a_reader_in_the_corpus_opens_the_composed_name"
R_NO_READER = "no_reader_in_the_corpus_opens_the_composed_name"
READER_VOCAB = (R_OPENS, R_NO_READER)

REACH_PROD = "reached_from_a_production_caller"
REACH_TEST = "reached_only_from_a_selftest_caller"
REACH_NONE = "no_python_caller_in_the_corpus"
REACH_VOCAB = (REACH_PROD, REACH_TEST, REACH_NONE)

V_NONE_OPENABLE = ("no_fixture_site_writes_into_a_directory_a_reader_in_the_corpus_opens_and_"
                   "the_sites_that_share_a_reader_name_share_only_the_name")
V_SOME_OPENABLE = "some_fixture_sites_write_into_a_repository_directory_and_a_reader_opens_that_name"
V_RUNTIME = ("every_fixture_site_takes_its_directory_from_a_name_so_the_census_cannot_say_where"
             "_it_lands")
V_EMPTY = "no_fixture_shaped_site_to_price"
VERDICT_VOCAB = (V_NONE_OPENABLE, V_SOME_OPENABLE, V_RUNTIME, V_EMPTY)

POPULATION_KEYS = ("corpus_sources", "fixture_sites")

TEMP_MARKERS = ("mkdtemp", "temporarydirectory", "tempfile", "tmpdir", "tmp_dir", "tempdir",
                "gettempdir", "namedtuple_tmp_placeholder_never_matches")
TEST_HINTS = ("selftest", "self_test", "test_", "_test", "smoke", "fixture")

READ_CALLS = {"read_text", "read_bytes", "load", "loads", "read_csv", "read_parquet",
              "read_json", "read_excel", "read_table"}
NAME_EXTS = (".json", ".jsonl", ".csv", ".parquet", ".md", ".txt", ".pkl", ".npz", ".html")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list[str]:
    """E428's scope, minus this study's own files (self-inclusion law, E180/E207)."""
    return [p for p in e428.corpus()
            if not os.path.basename(p).startswith(("e432", "_e432", "run_e432"))]


# ------------------------------------------------------------------ instrument: the directory

def supplied(site, index: dict[str, list[dict]]) -> list[tuple[dict, str]]:
    """(call row, the text this call passes for one of this site's directory parameters)."""
    out: list[tuple[dict, str]] = []
    rows = index.get(site.func) or []
    for param in site.parameter_directories():
        for row in rows:
            arg = e420.resolve_call_argument(row, param, site.params)
            if arg:
                out.append((row, arg))
    return out


def _is_literal(text: str) -> bool:
    """Is the whole supplied text one quoted string literal?

    A first draft asked whether the text *contains* a quote, which graded
    ``os.path.join(tmp, "ok")`` and ``item["nm"]`` as repository paths: the quote there is a
    suffix or a subscript key, not a directory the caller spells.  Only a lone literal counts.
    """
    text = text.strip()
    if len(text) < 2 or text[0] not in "'\"" or text[-1] != text[0]:
        return False
    inner = text[1:-1]
    return text[0] not in inner


def directory_class(pairs: list[tuple[dict, str]]) -> str:
    """temp / repo_relative / runtime_constant / never_supplied -- declared order."""
    if not pairs:
        return C_NEVER
    texts = [a for _, a in pairs]
    for text in texts:
        low = text.lower()
        if any(m in low for m in TEMP_MARKERS):
            return C_TEMP
    if any(_is_literal(a) for a in texts):
        return C_REPO
    return C_RUNTIME


def reachability(pairs, index: dict[str, list[dict]]) -> str:
    """A temp writer still executes: reachable is about the call sites, not about the disk."""
    if not index.get("__dummy__") and not pairs:
        return REACH_NONE
    callers = pairs or []
    if not callers:
        return REACH_NONE
    for row, _ in callers:
        hay = (row.get("caller") or "").lower() + " " + (row.get("file") or "").lower()
        if not any(h in hay for h in TEST_HINTS):
            return REACH_PROD
    return REACH_TEST


# ------------------------------------------------------------------ instrument: the reader side

def composed_names(site) -> list[str]:
    """File names this site composes, taken from the literal segments of its path."""
    out: list[str] = []
    for text, _ in site.paths:
        for ext in NAME_EXTS:
            for m in re.finditer(r"[A-Za-z0-9_%\.\-]+" + re.escape(ext), text):
                tok = m.group(0)
                if "%s" in tok or "%d" in tok or tok.startswith(ext):
                    continue
                out.append(tok)
    seen, uniq = set(), []
    for n in out:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq[:6]


def reader_index(sources: list[str], wanted: set[str]) -> list[dict]:
    """Every read call, in the files that spell one of the composed names.

    A full parse of 2,500 sources per pass is what made this study time out on its first run;
    the name is a literal in the file or it cannot match a call argument, so the text scan is a
    sound prefilter, not a shortcut that changes the population.
    """
    out: list[dict] = []
    for rel in sources:
        path = os.path.join(ROOT, rel)
        try:
            src = io.open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if not any(n in src for n in wanted):
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = e420.e419._call_name(node)
            if not name or name not in READ_CALLS:
                continue
            arg_text = ""
            if node.args:
                try:
                    arg_text = ast.get_source_segment(src, node.args[0]) or ""
                except Exception:  # source segment is best-effort, never fatal
                    arg_text = ""
            if not arg_text:
                continue
            out.append({"file": rel, "call": name,
                        "arg": arg_text[:200].replace("\n", " ")})
    return out


def readers_of(names: list[str], readers: list[dict]) -> list[dict]:
    """Readers whose argument spells the composed name as a whole path segment.

    A bare substring test matched ``status.json`` inside ``dashboard_status.json`` and turned
    nine temp-directory writers into "a reader opens this": the name is not a measurement unless
    it is a segment of the path, so the boundary is part of the gate.
    """
    if not names:
        return []
    patterns = [re.compile(r"(?:^|[/\\'\"])" + re.escape(n) + r"(?:$|[/\\'\"])") for n in names]
    hits = []
    for r in readers:
        if any(p.search(r["arg"]) for p in patterns):
            hits.append(r)
    return hits[:6]


# ------------------------------------------------------------------ build

def verdict_for(rows: list[dict]) -> str:
    """A shared file name is not a shared file: only a repository directory can be opened."""
    if not rows:
        return V_EMPTY
    if any(r["class"] == C_REPO and r["reader"] == R_OPENS for r in rows):
        return V_SOME_OPENABLE
    if all(r["class"] == C_RUNTIME for r in rows):
        return V_RUNTIME
    return V_NONE_OPENABLE


def build(cutoff: str | None = None) -> dict:
    face = _load(E428_FACE)
    cut = cutoff or face["evidence_cutoff"]
    published = [r for r in face["rows"] if r.get("fixture_shaped")]

    sources = corpus()
    sites, parsed = e420.scan_corpus(sources)
    flat = [s for found in sites.values() for s in found if s.parameter_directories()]
    by_key = {(s.path, s.func, s.line): s for s in flat}

    live_sites = [by_key[(p["file"], p["function"], p["line"])] for p in published
                  if (p["file"], p["function"], p["line"]) in by_key]
    wanted: set[str] = set()
    for site in live_sites:
        wanted.update(composed_names(site))
    # Only the 21 sites' own helpers are needed: E428's 97-name index is the wider instrument,
    # and rebuilding it costs minutes for call sites this study never reads.
    index = e420.main_call_index({s.func for s in live_sites}, sources)
    print(f"stage: {len(live_sites)} live sites, {len(wanted)} composed names, "
          f"{len(sources)} sources", flush=True)
    readers = reader_index(sources, wanted)

    rows: list[dict] = []
    missing: list[dict] = []
    for pub in published:
        key = (pub["file"], pub["function"], pub["line"])
        site = by_key.get(key)
        if site is None:
            missing.append({"file": pub["file"], "function": pub["function"],
                            "line": pub["line"],
                            "note": "published row is not a live parameter-directory site"})
            continue
        pairs = supplied(site, index)
        names = composed_names(site)
        hits = readers_of(names, readers)
        rows.append({
            "file": site.path,
            "function": site.func,
            "line": site.line,
            "write_call": site.call_name,
            "parameters": site.parameter_directories(),
            "class": directory_class(pairs),
            "reader": R_OPENS if hits else R_NO_READER,
            "reachable": reachability(pairs, index),
            "caller_sites": [{"file": r.get("file"), "caller": r.get("caller"),
                              "line": r.get("line"), "arg": a}
                             for r, a in pairs[:4]],
            "composed_names": names,
            "reader_sites": hits,
            "production_callers": sum(1 for r, _ in pairs
                                      if not any(h in ((r.get("caller") or "") + " " +
                                                       (r.get("file") or "")).lower()
                                                 for h in TEST_HINTS)),
        })
    rows.sort(key=lambda r: (r["class"], r["file"], r["line"]))

    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    by_reach: dict[str, int] = {}
    for r in rows:
        by_reach[r["reachable"]] = by_reach.get(r["reachable"], 0) + 1

    summary = {
        "fixture_sites_published_by_e428": len(published),
        "fixture_sites": len(rows),
        "rows_that_are_no_longer_a_live_site": len(missing),
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
        "corpus_sources": parsed,
        "reader_calls_scanned": len(readers),
        "population_premise_correction": {
            "pool_card_says": "21 fixture-shaped parameter-directory write sites among its 310",
            "measured": "the 21 are a subset of the 35 rows E428 could not place",
            "note": "E428 counted fixture_shaped over rows (the 35 unplaced), not over the 310",
        },
    }
    return {
        "study": "E432_which_fixture_shaped_parameter_write_site_is_read_by_a_published_reader",
        "card": "E432-WHICH-FIXTURE-SHAPED-PARAMETER-WRITE-SITE-IS-READ-BY-A-PUBLISHED-READER",
        "title": "price the 21 fixture-shaped parameter-directory write sites: where their "
                 "callers point them, and whether any reader in the corpus opens what they write",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(rows),
        "class_vocab": list(CLASS_VOCAB),
        "reader_vocab": list(READER_VOCAB),
        "reach_vocab": list(REACH_VOCAB),
        "population_keys": list(POPULATION_KEYS),
        "summary": summary,
        "rows": rows,
        "missing_rows": missing,
        "method_limits": [
            "directory_class reads the text a caller supplies, not the value at runtime: a "
            "caller that builds a temp directory through a helper named something else is "
            "graded runtime_constant, which is why that class is published rather than dropped",
            "reader detection is AST over read calls whose first argument spells the composed "
            "file name; a reader that composes the same name from parts does not match, so "
            "R_NO_READER means 'no reader spells this name', not 'nobody opens it'",
            "composed_names come from the literal segments of the write site's own path "
            "expression and may be a format template, in which case only the fixed chunks match",
            "reachability is a caller-file/function name heuristic on the same fixture hints the "
            "population used; no writer and no reader was run or edited",
        ],
    }


# ------------------------------------------------------------------ gates

def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face["rows"]
    s = face["summary"]
    if face["verdict"] not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    if face["verdict"] != verdict_for(rows):
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
    if sum(by_class.values()) != s.get("fixture_sites"):
        problems.append("row count does not equal fixture_sites")
    if s.get("fixture_sites") != len(rows):
        problems.append("summary fixture_sites differs from the row count")
    if s.get("fixture_sites") + s.get("rows_that_are_no_longer_a_live_site", 0) != \
            s.get("fixture_sites_published_by_e428"):
        problems.append("published population does not equal live rows + missing rows")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, "fixturewrite_latest.json"))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append(f"live verdict {live['verdict']} != published {face['verdict']}")
    if live["summary"]["by_class"] != face["summary"]["by_class"]:
        problems.append("live by_class differs from the published face")
    if live["summary"]["fixture_sites"] != face["summary"]["fixture_sites"]:
        problems.append("live fixture_sites differs from the published face")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    # Leg 1-4: the directory classifier, one fixture per state.
    class Row(dict):
        pass

    check("temp", directory_class([({"caller": "x", "file": "y"}, "tempfile.mkdtemp()")])
          == C_TEMP)
    check("repo", directory_class([({"caller": "x", "file": "y"}, '"results/x"')]) == C_REPO)
    check("runtime", directory_class([({"caller": "x", "file": "y"}, "OUTDIR")]) == C_RUNTIME)
    check("never", directory_class([]) == C_NEVER)

    # Leg 5: a temp marker under a quoted string is still temp (order of the declared classes).
    check("temp beats literal",
          directory_class([({"caller": "x", "file": "y"}, "'tempfile.mkdtemp(/x)'")]) == C_TEMP)

    # Leg 6-7: reachability separates a production caller from a selftest-only one.
    check("prod", reachability([({"caller": "run_all", "file": "scripts/a.py"}, "d")], {})
          == REACH_PROD)
    check("test", reachability([({"caller": "run_selftest", "file": "scripts/a.py"}, "d")], {})
          == REACH_TEST)

    # Leg 8: no supplied argument is no caller, not a test caller.
    check("none", reachability([], {}) == REACH_NONE)

    # Leg 9: composed names keep fixed chunks and drop format templates.
    class FakeSite:
        paths = [("dir/x.json", None), ("%s.json" % ("a",), None), ("p/face-%s.json" % "b",
                                                                    None)]

    names = composed_names(FakeSite())
    check("name x.json", "x.json" in names)
    check("template dropped", not any("%s" in n for n in names))

    # Leg 10-12: verdict recomputation refuses a hand-written table.
    base = {"file": "f", "function": "g", "line": 1, "reader": R_NO_READER,
            "reachable": REACH_TEST}
    check("temp is none openable",
          verdict_for([dict(base, **{"class": C_TEMP})]) == V_NONE_OPENABLE)
    check("some repo read", verdict_for([dict(base, **{"class": C_REPO,
                                                      "reader": R_OPENS})]) == V_SOME_OPENABLE)
    check("runtime", verdict_for([dict(base, **{"class": C_RUNTIME})]) == V_RUNTIME)
    check("a shared name is not openable",
          verdict_for([dict(base, **{"class": C_TEMP, "reader": R_OPENS})]) == V_NONE_OPENABLE)
    check("empty", verdict_for([]) == V_EMPTY)

    # Leg 13: a doctored by_class must be caught by the tally.
    face = {"rows": [dict(base, **{"class": C_TEMP, "caller_sites": [{}],
                                   "reader_sites": [], "parameters": []})],
            "verdict": V_NONE_OPENABLE,
            "summary": {"by_class": {C_TEMP: 2}, "by_reachable": {REACH_TEST: 1},
                        "fixture_sites": 1, "fixture_sites_published_by_e428": 1,
                        "rows_that_are_no_longer_a_live_site": 0}}
    check("doctored tally caught", bool(tally_problems(face)))
    face["summary"]["by_class"] = {C_TEMP: 1}
    check("clean tally passes", not tally_problems(face))

    # Leg 17-18: only a lone quoted literal is a repository directory.  Both shapes below were
    # graded repo_relative by the first draft and are the two rows that created a false verdict.
    check("quote suffix is not a path", not _is_literal('os.path.join(tmp, "ok")'))
    check("subscript key is not a path", not _is_literal('item["nm"]'))
    check("lone literal is a path", _is_literal('"results/x"'))

    # Leg 19: a reader must spell the name as a segment, not inside another name.
    readers = [{"file": "a.py", "call": "load", "arg": 'open("results/dashboard_status.json")'}]
    check("substring is not a segment", readers_of(["status.json"], readers) == [])
    readers2 = [{"file": "a.py", "call": "load", "arg": 'open("results/status.json")'}]
    check("segment matches", len(readers_of(["status.json"], readers2)) == 1)

    for f in fails:
        print(f"[FAIL] {f}")
    print(f"selftest {legs - len(fails)}/{legs}")
    return 0 if not fails else 1


def write_face(face: dict) -> str:
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    day = face["evidence_cutoff"]
    name = f"FIXTUREWRITE-{day}.json"
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for target in (os.path.join(OUTDIR, name),
                   os.path.join(OUTDIR, "fixturewrite_latest.json")):
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
    print(f"fixture_sites={s['fixture_sites']} by_class={s['by_class']} "
          f"by_reach={s['by_reachable']} readers={s['by_reader']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))