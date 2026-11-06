"""E482 -- do the ``*_latest.json`` spellings opened outside the 36 twin families exist?

E479 published its population as the 36 family-named twins and then reported, as a witness that
its scan was not blind, that 147 sources make 689 opener sites naming a ``*_latest.json`` that
belongs to none of those families.  Those sites were counted and dropped.  A site that opens a
spelling no file carries is a reader of a face that may not exist, so each of them is priced
here: the literal is resolved against the tree and the spelling is joined to the sources that
write it.

Run:      python scripts/e482_latest_outside.py run
Verify:   python scripts/e482_latest_outside.py verify   (re-derives from the live tree)
Check:    python scripts/e482_latest_outside.py check    (tallies re-derive from the face)
Selftest: python scripts/e482_latest_outside.py selftest
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
import e468_pointer_reach as e468  # noqa: E402
import e470_target_read as e470  # noqa: E402
import e479_twin_read as e479  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "latestoutside_latest.json"
DATED_PREFIX = "LATESTOUTSIDE"
CARD = ("E482-WHICH-OF-THE-LATEST-SPELLINGS-OPENED-OUTSIDE-THE-36-TWIN-FAMILIES-RESOLVE-TO-A-"
        "FILE-THAT-EXISTS")

PARENT_FACE = "twinread_latest.json"         # E479: the 36 twins and the outside-spelling witness
SUFFIX = "_latest.json"

# own outputs and their runners are excluded so the census cannot count itself (E180/E207 family)
SELF_PREFIX = ("e479_", "run_e479", "e480_", "run_e480", "e481_", "run_e481", "e482_",
               "run_e482", "e484_", "run_e484")

# ---- resolution tiers -------------------------------------------------------------------------
R_LITERAL = "the_literal_names_a_path_that_exists_on_disk"
R_TAIL = "the_literal_names_a_path_that_does_not_exist_but_a_file_ends_with_it"
R_SINGLE = "a_bare_basename_and_exactly_one_file_in_the_tree_carries_it"
R_SEVERAL = "a_bare_basename_and_several_files_in_the_tree_carry_it_so_the_directory_is_unproved"
R_TEMPLATE = "the_spelling_carries_no_concrete_name_so_it_cannot_resolve_to_one_file"
R_NONE = "no_file_in_the_tree_carries_this_spelling"
TIERS = (R_LITERAL, R_TAIL, R_SINGLE, R_SEVERAL, R_TEMPLATE, R_NONE)
EXISTS_TIERS = (R_LITERAL, R_TAIL, R_SINGLE, R_SEVERAL)

# ---- per-spelling classes ---------------------------------------------------------------------
C_FILE_WRITER = "a_file_carries_this_spelling_and_a_source_writes_it"
C_FILE_NO_WRITER = "a_file_carries_this_spelling_but_no_source_writes_it"
C_DEAD_WRITER = "no_file_carries_this_spelling_although_a_source_writes_it"
C_DEAD_NO_WRITER = "no_file_carries_this_spelling_and_no_source_writes_it"
C_TEMPLATE = "the_spelling_names_no_concrete_file_at_all"
CLASSES = (C_FILE_WRITER, C_FILE_NO_WRITER, C_DEAD_WRITER, C_DEAD_NO_WRITER, C_TEMPLATE)

# ---- verdicts ---------------------------------------------------------------------------------
V_EMPTY = "no_latest_spelling_is_opened_outside_the_twin_population"
V_ALL = "every_outside_latest_spelling_that_is_opened_resolves_to_a_file_on_disk"
V_NONE = "no_outside_latest_spelling_that_is_opened_resolves_to_a_file_on_disk"
V_MOST_LIVE = "most_outside_opener_sites_resolve_to_a_file_but_some_open_a_spelling_no_file_carries"
V_MOST_DEAD = "most_outside_opener_sites_open_a_spelling_no_file_carries"
VERDICT_VOCAB = (V_EMPTY, V_ALL, V_NONE, V_MOST_LIVE, V_MOST_DEAD)

MAX_READ_BYTES = 2 * 1024 * 1024
MAX_PATHS_PER_ROW = 12
INDEX_SKIP_DIRS = (".git", ".codely-cli", "_smoke", "_quarantine", "__pycache__", "node_modules")


def _norm(text):
    return str(text or "").replace("\\", "/").strip()


def _is_self(rel):
    return os.path.basename(rel).startswith(SELF_PREFIX)


def _source_text(path):
    return e451.read_text(path)


def _concrete_name(base):
    """``BASISRECOVERY_latest.json`` -> 'basisrecovery'; ``_latest.json`` -> '' (no name)."""
    return base[: -len(SUFFIX)].strip("_").lower()


def _is_template(base):
    if "%" in base or "{" in base or "$" in base:
        return True
    return not _concrete_name(base)


# ------------------------------------------------------------------ population


def population(root=None):
    """E479's published outside-spelling witness counts, read as the parent's contract."""
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    face = json.load(io.open(path, "r", encoding="utf-8"))
    summary = face.get("summary") or {}
    twins = {}
    for row in face.get("rows") or []:
        twin = _norm(row.get("twin"))
        if twin:
            twins[os.path.basename(twin).lower()] = twin
    return twins, {
        "face": PARENT_FACE,
        "face_verdict": face.get("verdict"),
        "face_evidence_cutoff": face.get("evidence_cutoff"),
        "parent_twins": len(twins),
        "parent_sources_naming_an_outside_spelling": summary.get(
            "sources_naming_a_latest_spelling_outside_this_population"),
        "parent_opener_sites_naming_an_outside_spelling": summary.get(
            "opener_sites_naming_a_latest_spelling_outside_this_population"),
    }


def file_index(root=None):
    """{lowercased basename: [repo-relative paths]} over every file in the tree, names only."""
    root = root or ROOT
    index = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in INDEX_SKIP_DIRS]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")
            index.setdefault(name.lower(), []).append(rel)
    for key in index:
        index[key].sort()
    return index


# ------------------------------------------------------------------ scan


def scan(root=None, twin_basenames=None):
    """Every opener site spelling a ``*_latest.json`` outside the twin population.

    Same call shape as E479 (e470's name resolution, one AST hop from the opener), so the two
    faces are comparable; the difference is that a site outside the population is now a row.
    Write literals are collected in the same pass so a spelling can be joined to its producer
    without a second walk.
    """
    root = root or ROOT
    twin_basenames = twin_basenames or {}
    sites = []
    writers = {}
    scanned = 0
    for rel in e468._walk_py(root):
        if _is_self(rel):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = _source_text(path)
        except OSError:
            continue
        low = text.lower()
        if SUFFIX not in low:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        scanned += 1
        assigned = e470._assignments(tree)
        for lit in e479._write_literals(tree):
            base = os.path.basename(_norm(lit)).lower()
            if base.endswith(SUFFIX) and base not in twin_basenames:
                writers.setdefault(base, set()).add(rel)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not e470._is_opener(node):
                continue
            for lit in e470._evidence(node, assigned):
                base = os.path.basename(_norm(lit)).lower()
                if not base.endswith(SUFFIX) or base in twin_basenames:
                    continue
                sites.append({
                    "source": rel,
                    "line": getattr(node, "lineno", 0),
                    "literal": lit,
                    "spelling": base,
                })
    # one site per (source, line, literal): the same call can surface the same literal twice.
    # E479 counted OCCURRENCES, not triples, so its site tally is larger on the same tree; the
    # source tally is the number that has to agree, and both are published.
    raw_count = len(sites)
    seen, uniq = set(), []
    for s in sorted(sites, key=lambda r: (r["spelling"], r["source"], r["line"], r["literal"])):
        sig = (s["source"], s["line"], s["literal"])
        if sig in seen:
            continue
        seen.add(sig)
        uniq.append(s)
    out_writers = {k: sorted(v) for k, v in writers.items()}
    return uniq, out_writers, {"sources_scanned_mentioning_the_suffix": scanned,
                               "raw_site_occurrences": raw_count}


def resolve(root, literal, index):
    """How one opener literal meets the tree.  Returns (tier, resolved paths)."""
    lit = _norm(literal)
    base = os.path.basename(lit).lower()
    if _is_template(base):
        return R_TEMPLATE, []
    if os.path.isabs(lit) or ":" in lit.split("/")[0]:
        if os.path.exists(lit):
            return R_LITERAL, [lit]
        return R_NONE, []
    if "/" in lit:
        if os.path.exists(os.path.join(root, *lit.split("/"))):
            return R_LITERAL, [lit.lstrip("./")]
        tail = lit.lower().lstrip("./")
        hits = [p for p in index.get(base, []) if p.lower().endswith(tail)]
        if not hits:
            # the literal names a directory nothing has, but a file with that basename is on
            # disk somewhere: existence is proved, the address is not (E366's two address forms)
            hits = list(index.get(base, []))
        if hits:
            return R_TAIL, hits
        return R_NONE, []
    hits = index.get(base, [])
    if len(hits) == 1:
        return R_SINGLE, hits
    if hits:
        return R_SEVERAL, hits
    return R_NONE, []


def classify(root=None, rows_input=None):
    """One row per distinct spelling, with its sites, its tier census and its producers."""
    root = root or ROOT
    sites, writers, meta = scan(root) if rows_input is None else (rows_input[0], rows_input[1],
                                                                  rows_input[2])
    index = file_index(root)
    by_spelling = {}
    for s in sites:
        slot = by_spelling.setdefault(s["spelling"], {"sites": [], "tiers": {}})
        tier, paths = resolve(root, s["literal"], index)
        slot["sites"].append({
            "source": s["source"],
            "line": s["line"],
            "literal": s["literal"],
            "tier": tier,
            "resolved_paths": paths[:MAX_PATHS_PER_ROW],
            "files_found": len(paths),
        })
        slot["tiers"][tier] = slot["tiers"].get(tier, 0) + 1
    rows = []
    for spelling in sorted(by_spelling):
        slot = by_spelling[spelling]
        site_rows = slot["sites"]
        tiers = {k: slot["tiers"].get(k, 0) for k in TIERS}
        exists = any(t in EXISTS_TIERS for t in tiers for _ in [0] if tiers[t])
        row_writers = writers.get(spelling) or []
        if tiers[R_TEMPLATE] == len(site_rows):
            klass = C_TEMPLATE
        elif exists and row_writers:
            klass = C_FILE_WRITER
        elif exists:
            klass = C_FILE_NO_WRITER
        elif row_writers:
            klass = C_DEAD_WRITER
        else:
            klass = C_DEAD_NO_WRITER
        paths = sorted({p for s in site_rows for p in s["resolved_paths"]})
        rows.append({
            "spelling": spelling,
            "class": klass,
            "site_count": len(site_rows),
            "sources": sorted({s["source"] for s in site_rows}),
            "tier_counts": tiers,
            "files_on_disk_for_this_spelling": len(index.get(spelling, [])),
            "resolved_paths": paths[:MAX_PATHS_PER_ROW],
            "writers": row_writers,
            "sites": site_rows,
        })
    return rows, meta


# ------------------------------------------------------------------ verdict / summary


def _recompute(face):
    rows = face.get("rows") or []
    site_counts = {}
    for row in rows:
        site_counts[row.get("class")] = site_counts.get(row.get("class"), 0) + 1
    site_counts = {k: site_counts.get(k, 0) for k in CLASSES}
    dead_classes = (C_DEAD_WRITER, C_DEAD_NO_WRITER, C_TEMPLATE)
    dead_rows = [r for r in rows if r.get("class") in dead_classes]
    live_rows = [r for r in rows if r.get("class") not in dead_classes]
    return {
        "distinct_spellings": len(rows),
        "opener_sites": sum(int(r.get("site_count") or 0) for r in rows),
        "sources_holding_an_opener_site": len({s for r in rows for s in (r.get("sources") or [])}),
        "class_counts": site_counts,
        "spellings_that_resolve_to_a_file": len(live_rows),
        "spellings_that_resolve_to_no_file": len(dead_rows),
        "spellings_with_a_writer": sum(1 for r in rows if r.get("writers")),
        "spellings_without_a_writer": sum(1 for r in rows if not r.get("writers")),
        "sites_on_spellings_that_resolve": sum(int(r.get("site_count") or 0) for r in live_rows),
        "sites_on_spellings_that_resolve_to_nothing": sum(int(r.get("site_count") or 0)
                                                         for r in dead_rows),
        "sites_on_a_spelling_a_source_writes": sum(int(r.get("site_count") or 0) for r in rows
                                                   if r.get("writers")),
        "sites_on_a_spelling_no_source_writes": sum(int(r.get("site_count") or 0) for r in rows
                                                    if not r.get("writers")),
        "template_spellings": sum(int(r.get("tier_counts", {}).get(R_TEMPLATE) or 0)
                                  for r in rows if r.get("class") == C_TEMPLATE),
    }


def _verdict(summary):
    if not summary.get("distinct_spellings"):
        return V_EMPTY
    live = int(summary.get("sites_on_spellings_that_resolve") or 0)
    dead = int(summary.get("sites_on_spellings_that_resolve_to_nothing") or 0)
    if dead == 0:
        return V_ALL
    if live == 0:
        return V_NONE
    return V_MOST_LIVE if live >= dead else V_MOST_DEAD


# ------------------------------------------------------------------ build


def build(root=None, write=True):
    root = root or ROOT
    twin_basenames, parent = population(root)
    sites, writers, site_meta = scan(root, twin_basenames)
    rows, _ = classify(root, (sites, writers, site_meta))
    summary = _recompute({"rows": rows})
    summary["parent_sources_naming_an_outside_spelling"] = parent[
        "parent_sources_naming_an_outside_spelling"]
    summary["parent_opener_sites_naming_an_outside_spelling"] = parent[
        "parent_opener_sites_naming_an_outside_spelling"]
    summary["raw_site_occurrences_on_this_tree"] = site_meta.get("raw_site_occurrences")
    summary["parent_source_count_reproduced"] = (
        summary["parent_sources_naming_an_outside_spelling"]
        == summary["sources_holding_an_opener_site"])
    summary["parent_site_count_relation"] = (
        "the_parent_counts_literal_occurrences_this_face_counts_distinct_source_line_literal_"
        "triples_so_the_two_site_tallies_are_not_the_same_measurement")
    face = {
        "card": CARD,
        "study": "E482_which_latest_spellings_opened_outside_the_twin_families_resolve_to_a_file",
        "title": ("which of the latest spellings opened outside the 36 twin families resolve to a "
                  "file that exists?"),
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": {
            "face": parent["face"],
            "face_evidence_cutoff": parent["face_evidence_cutoff"],
            "face_verdict": parent["face_verdict"],
            "parent_twins": parent["parent_twins"],
            "parent_sources_naming_an_outside_spelling": parent[
                "parent_sources_naming_an_outside_spelling"],
            "parent_opener_sites_naming_an_outside_spelling": parent[
                "parent_opener_sites_naming_an_outside_spelling"],
            "sources_scanned_mentioning_the_suffix": site_meta[
                "sources_scanned_mentioning_the_suffix"],
        },
        "evidence_definition": {
            R_LITERAL: "the literal carries a directory and that path exists under the repo root",
            R_TAIL: "the literal carries a directory that does not exist, but a file with that "
                    "basename is on disk somewhere (existence proved, address not proved)",
            R_SINGLE: "the literal is a bare basename and exactly one file in the tree has it",
            R_SEVERAL: "the literal is a bare basename and several files have it: existence is "
                       "proved, the directory is not (E366's two address forms)",
            R_TEMPLATE: "the spelling has no concrete name ('%s_latest.json', '_latest.json'), so "
                        "no single file can be the thing it names",
            R_NONE: "nothing in the tree carries this spelling",
        },
        "class_definition": {
            C_FILE_WRITER: "some site resolves to a file and a source writes that spelling",
            C_FILE_NO_WRITER: "some site resolves to a file that no source in the corpus writes",
            C_DEAD_WRITER: "no site resolves but a source writes the spelling: the reader and the "
                           "writer disagree about the path, or the writer has not run yet",
            C_DEAD_NO_WRITER: "no site resolves and no source writes it: a reader of a face "
                              "nothing produces",
            C_TEMPLATE: "every site for this spelling is a template that carries no name",
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "the population is E479's rule: an opener literal whose basename ends in "
            "'_latest.json' and belongs to none of the 36 twins. A plain 'latest.json' does not "
            "end with the suffix and is not in this population (its own census is E417's)",
            "existence is judged against the tree as it stands at run time; a writer that has not "
            "run yet produces a dead_read_writer row, and the class says which of the two it is",
            "a bare basename is proved to exist but never proved to be the file the reader means "
            "(E366); the row publishes how many files carry it",
            "the scan reads .py sources that mention the suffix and follows e470's one-hop name "
            "resolution, so a path composed through an argument or an environment variable is "
            "invisible",
            "this census excludes its own runner and the E479/E480/E481/E484 families so it cannot "
            "count its own literals (E180/E207 family)",
            "the parent published 689 opener sites where this face counts distinct "
            "(source, line, literal) triples: the two site tallies are different measurements, "
            "and only the source tally (147) is compared",
            "resolving a spelling to a file is not the same as reading its content; E477/E478/E481 "
            "own what the bytes cost and whether two vintages agree",
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
    for row in face.get("rows") or []:
        spelling = row.get("spelling")
        if row.get("class") not in CLASSES:
            problems.append("%s: unknown class %r" % (spelling, row.get("class")))
        sites = row.get("sites") or []
        if row.get("site_count") != len(sites):
            problems.append("%s: site_count %r but %d sites"
                            % (spelling, row.get("site_count"), len(sites)))
        tiers = row.get("tier_counts") or {}
        if sum(int(tiers.get(k) or 0) for k in TIERS) != len(sites):
            problems.append("%s: tier counts do not sum to the sites" % (spelling,))
        for s in sites:
            if s.get("tier") not in TIERS:
                problems.append("%s: unknown tier %r" % (spelling, s.get("tier")))
            if s.get("files_found") != len(s.get("resolved_paths") or []) \
                    and int(s.get("files_found") or 0) <= MAX_PATHS_PER_ROW:
                problems.append("%s: files_found %r but %d paths"
                                % (spelling, s.get("files_found"),
                                   len(s.get("resolved_paths") or [])))
        exists = any(int(tiers.get(k) or 0) for k in EXISTS_TIERS)
        if row.get("class") == C_TEMPLATE and int(tiers.get(R_TEMPLATE) or 0) != len(sites):
            problems.append("%s: template class beside a non-template site" % (spelling,))
        if row.get("class") == C_FILE_WRITER and not (exists and row.get("writers")):
            problems.append("%s: file+writer class without both" % (spelling,))
        if row.get("class") == C_FILE_NO_WRITER and not exists:
            problems.append("%s: file class with no resolving site" % (spelling,))
        if row.get("class") == C_DEAD_WRITER and (exists or not row.get("writers")):
            problems.append("%s: dead+writer class does not fit" % (spelling,))
        if row.get("class") == C_DEAD_NO_WRITER and (exists or row.get("writers")):
            problems.append("%s: dead+no-writer class does not fit" % (spelling,))
    if summary.get("verdict") is not None:
        problems.append("summary must not carry a verdict")
    if _verdict({k: summary.get(k) for k in derived}) != face.get("verdict"):
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"), _verdict({k: summary.get(k) for k in derived})))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e482 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    print("spellings=%d sites=%d resolve=%d dead=%d"
          % (face["summary"]["distinct_spellings"], face["summary"]["opener_sites"],
             face["summary"]["sites_on_spellings_that_resolve"],
             face["summary"]["sites_on_spellings_that_resolve_to_nothing"]))
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
        problems.append("spelling population moved: +%d -%d"
                        % (len(set(b) - set(a)), len(set(a) - set(b))))
    for spelling in sorted(set(a) & set(b)):
        for key in ("class", "site_count", "files_on_disk_for_this_spelling"):
            if a[spelling].get(key) != b[spelling].get(key):
                problems.append("%s: %s moved %r -> %r"
                                % (spelling, key, a[spelling].get(key), b[spelling].get(key)))
    problems.extend(row_problems(fresh))
    print("e482 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    """A tiny tree exercising every tier and every class."""
    os.makedirs(os.path.join(root, "results", "state_tilt"))
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "results", "alpha"))
    os.makedirs(os.path.join(root, "results", "beta"))
    # one file for the single-basename tier, two for the several-basename tier
    io.open(os.path.join(root, "results", "alpha", "known_latest.json"), "w",
            encoding="utf-8").write("{}")
    io.open(os.path.join(root, "results", "beta", "produced_latest.json"), "w",
            encoding="utf-8").write("{}")
    for d in ("alpha", "beta"):
        io.open(os.path.join(root, "results", d, "shared_latest.json"), "w",
                encoding="utf-8").write("{}")
    # parent face: one twin, so it is excluded from the population
    parent = {
        "verdict": "some_twins_are_opened_by_a_source_that_writes_neither_them_nor_their_family",
        "evidence_cutoff": "2026-11-07",
        "summary": {"sources_naming_a_latest_spelling_outside_this_population": 3,
                    "opener_sites_naming_a_latest_spelling_outside_this_population": 4},
        "rows": [{"twin": "results/alpha/twin_latest.json"}],
    }
    io.open(os.path.join(root, "results", "state_tilt", "twinread_latest.json"), "w",
            encoding="utf-8").write(json.dumps(parent))
    body = (
        "import json, os\n"
        "HERE = 'results/alpha'\n"
        "A = os.path.join(HERE, 'known_latest.json')\n"
        "json.load(open(A))\n"                          # R_LITERAL (via a name)
        "json.load(open('results/alpha/shared_latest.json'))\n"   # R_LITERAL
        "json.load(open('shared_latest.json'))\n"       # R_SEVERAL
        "json.load(open('%s_latest.json' % 'x'))\n"     # R_TEMPLATE
        "json.load(open('results/gamma/twin_latest.json'))\n"     # excluded (twin)
        "json.load(open('results/gamma/ghost_latest.json'))\n"    # R_NONE
        "open('results/beta/written_latest.json', 'w').write('{}')\n"  # writer, file absent
        "open('results/beta/produced_latest.json', 'w').write('{}')\n"  # writer, file present
    )
    io.open(os.path.join(root, "scripts", "reader.py"), "w", encoding="utf-8").write(body)
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e482_")
    try:
        root = _fixture(tmp)
        twins, parent = population(root)
        leg("parent twin is read as an exclusion", "results/alpha/twin_latest.json" in twins.values()
            or "twin_latest.json" in twins)
        sites, writers, meta = scan(root, twins)
        spellings = sorted({s["spelling"] for s in sites})
        leg("twin spelling is not in the population", "twin_latest.json" not in spellings)
        leg("six outside spellings are found",
            spellings == ["%s_latest.json", "ghost_latest.json", "known_latest.json",
                          "produced_latest.json", "shared_latest.json",
                          "written_latest.json"])
        index = file_index(root)
        leg("single basename resolves to one file",
            len(index.get("known_latest.json") or []) == 1)
        leg("shared basename is carried by two files",
            len(index.get("shared_latest.json") or []) == 2)
        tier, paths = resolve(root, "known_latest.json", index)
        leg("bare basename tier", tier == R_SINGLE and len(paths) == 1)
        tier, paths = resolve(root, "shared_latest.json", index)
        leg("several-files tier", tier == R_SEVERAL and len(paths) == 2)
        tier, _ = resolve(root, "results/alpha/shared_latest.json", index)
        leg("literal path exists", tier == R_LITERAL)
        tier, _ = resolve(root, "nowhere/shared_latest.json", index)
        leg("missing directory falls back to the tail", tier == R_TAIL)
        tier, _ = resolve(root, "ghost_latest.json", index)
        leg("nothing carries it", tier == R_NONE)
        tier, _ = resolve(root, "%s_latest.json", index)
        leg("template carries no name", tier == R_TEMPLATE)
        leg("writer of a spelling is seen", "written_latest.json" in writers)
        rows, _ = classify(root, (sites, writers, meta))
        by = {r["spelling"]: r for r in rows}
        leg("file + writer class",
            by["produced_latest.json"]["class"] == C_FILE_WRITER and
            by["known_latest.json"]["class"] == C_FILE_NO_WRITER)
        leg("file without a writer class",
            by["shared_latest.json"]["class"] == C_FILE_NO_WRITER and
            by["shared_latest.json"]["files_on_disk_for_this_spelling"] == 2)
        leg("dead + writer class", by["written_latest.json"]["class"] == C_DEAD_WRITER)
        leg("dead + no writer class", by["ghost_latest.json"]["class"] == C_DEAD_NO_WRITER)
        leg("template class", by["%s_latest.json"]["class"] == C_TEMPLATE)
        face = {"rows": rows, "evidence_cutoff": "2026-11-07"}
        summary = _recompute(face)
        face["summary"] = summary
        face["verdict"] = _verdict(summary)
        leg("tallies re-derive", _recompute(face)["opener_sites"] == summary["opener_sites"])
        leg("no row problems on the fixture", row_problems(face) == [])
        broken = json.loads(json.dumps(face))
        broken["rows"][0]["site_count"] += 1
        leg("a moved site count is refused", row_problems(broken))
        broken2 = json.loads(json.dumps(face))
        for r in broken2["rows"]:
            if r["class"] == C_DEAD_NO_WRITER:
                r["class"] = C_FILE_WRITER
        leg("a class that contradicts its own sites is refused", row_problems(broken2))
        broken3 = json.loads(json.dumps(face))
        broken3["verdict"] = V_ALL
        leg("a verdict that does not re-derive is refused", row_problems(broken3))
        leg("write leaves both faces on disk",
            all(os.path.exists(p) for p in _write(face, root)))
    finally:
        pass
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def run(root=None):
    root = root or ROOT
    face = build(root, write=True)
    summary = face["summary"]
    print("e482 run verdict=%s" % face["verdict"])
    print("spellings=%d sites=%d sources=%d"
          % (summary["distinct_spellings"], summary["opener_sites"],
             summary["sources_holding_an_opener_site"]))
    print("resolve=%d dead=%d template_sites=%d source_count_reproduced=%s"
          % (summary["sites_on_spellings_that_resolve"],
             summary["sites_on_spellings_that_resolve_to_nothing"],
             summary["template_spellings"], summary["parent_source_count_reproduced"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E482 outside-population latest spellings")
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