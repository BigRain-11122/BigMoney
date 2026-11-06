"""E470 -- is the target of a pointer that needs another base ever opened at all?

E468 asked which sources NAME the 37 pointer targets that need a base other than the repo root and
published the naming residue: 24 targets are named by no source, 8 naming sites belong to the
producer that writes the target, 4 rows only a one-off round script names and 2 only a smoke leg.
Naming is not reading (E207 / E466 / E436).  This study asks the other question: for each target,
is there a site that turns it into a path the program can OPEN?

Four channels, each published apart:

  OPENER   a call that opens a path -- open / io.open / Path.read_text / json.load(yaml.load) /
           pandas.read_* / gzip.open.  The path evidence is the string literals in the call and the
           literals assigned to any name the call mentions (one hop, published as a method limit).
  MATCH    how the evidence spells the target: the whole repo-relative path, a composed tail
           (``state_tilt/FOO.json``), or only the basename (which proves the name, not the base).
  GLOB     a glob()/iglob()/rglob()/Path.glob() pattern that matches the target per segment
           ('*' inside a segment, '**' across segments) and carries at least one literal segment.
  KEYREAD  a module that opens the pointing face itself and carries the pointer key literal --
           the only site that could follow the pointer rather than guess the file.
  PRODUCER the script that WRITES the target (E464 write_sites via e468.producer_map).

The residue is the answer: targets only their own writer opens, targets an unrelated study opens,
targets only a glob lands on, and targets no site in the corpus ever opens.

Run:      python scripts/e470_target_read.py run
Verify:   python scripts/e470_target_read.py verify   (re-derives from the live tree)
Check:    python scripts/e470_target_read.py check    (tallies re-derive from the face)
Selftest: python scripts/e470_target_read.py selftest
"""

import argparse
import ast
import datetime
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (read_text)
import e464_producer_intent as e464  # noqa: E402  (face_stem -- the stem rule the writer map uses)
import e466_pointer_join as e466  # noqa: E402  (B_ROOT)
import e468_pointer_reach as e468  # noqa: E402  (population / producer_map / _walk_py / _alias_stems)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "targetread_latest.json"
DATED_PREFIX = "TARGETREAD"
CARD = "E470-IS-THE-TARGET-OF-A-POINTER-THAT-NEEDS-ANOTHER-BASE-EVER-READ-AT-ALL"
SOURCE_FACE = os.path.join(OUTDIR, "pointerreach_latest.json")

# own outputs and their runners are excluded so the census cannot count itself (E180/E207 family)
SELF_SKIP = ("e461_", "e462_", "e463_", "e464_", "e466_", "e468_", "e470_",
             "run_e461", "run_e462", "run_e463", "run_e464", "run_e466", "run_e468", "run_e470")
MAX_READ_BYTES = 2 * 1024 * 1024
NAME_HOPS = 4

# ---- opener vocabulary ---------------------------------------------------------------------
OPEN_FUNCS = ("open", "loadtxt", "genfromtxt")
OPEN_ATTRS = ("open", "read_text", "read_bytes", "read_csv", "read_json", "read_parquet",
              "read_excel", "read_table", "load")
GLOB_FUNCS = ("glob", "iglob", "rglob")

# ---- match kinds ---------------------------------------------------------------------------
M_EXACT = "the_whole_repo_relative_path"
M_TAIL = "a_composed_tail_that_ends_with_the_target_path"
M_BASENAME = "only_the_basename_the_base_is_not_proven"
MATCH_KINDS = (M_EXACT, M_TAIL, M_BASENAME)

# ---- residues ------------------------------------------------------------------------------
R_OTHER = "opened_by_a_study_that_writes_neither_this_target_nor_the_pointing_face"
R_PRODUCER = "opened_only_by_the_script_that_writes_it"
R_SMOKE = "opened_only_by_a_smoke_or_runner_leg"
R_ROUND = "opened_only_by_a_one_off_round_script"
R_GLOB = "reached_only_through_a_glob_or_a_directory_prefix"
R_NEVER = "never_opened_by_any_site_in_the_corpus"
RESIDUES = (R_OTHER, R_PRODUCER, R_SMOKE, R_ROUND, R_GLOB, R_NEVER)

V_EMPTY = "the_pointer_face_published_no_target_that_needs_another_base"
V_ALL_PRODUCER = "every_target_that_needs_another_base_is_opened_only_by_the_script_that_writes_it"
V_SOME_OTHER = ("some_targets_that_need_another_base_are_opened_by_a_study_that_writes_neither_"
                "the_target_nor_the_pointing_face")
V_SOME_GLOB = "some_targets_that_need_another_base_are_reached_only_through_a_glob"
V_SOME_NEVER = "some_targets_that_need_another_base_are_never_opened_by_any_site"
VERDICT_VOCAB = (V_EMPTY, V_ALL_PRODUCER, V_SOME_OTHER, V_SOME_GLOB, V_SOME_NEVER)


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _now():
    return datetime.datetime.now().astimezone()


def _today():
    return _now().strftime("%Y-%m-%d")


def _norm(text):
    return str(text).replace("\\", "/").strip()


# ------------------------------------------------------------------ population


def population(root=None):
    """The distinct targets E468 published, each carrying the pointers that name it."""
    root = root or ROOT
    face = _load(os.path.join(root, "results", "state_tilt", "pointerreach_latest.json"))
    by_target = {}
    for row in face.get("rows") or []:
        tgt = row.get("target")
        if not tgt:
            continue
        slot = by_target.setdefault(tgt, {"target": tgt, "basename": os.path.basename(tgt),
                                          "pointers": []})
        slot["pointers"].append({"face": row.get("face"), "key": row.get("key"),
                                 "value": row.get("value"), "spelling": row.get("spelling"),
                                 "required_base": row.get("required_base")})
    out = sorted(by_target.values(), key=lambda r: r["target"])
    return out, {"source_face_pointers": len(face.get("rows") or []),
                 "source_face_verdict": face.get("verdict")}


def spellings(target, root=None):
    """Every way a literal may spell this target, longest first (exact wins over tail)."""
    root = root or ROOT
    root_norm = _norm(root)
    out = [_norm(target)]
    if _norm(target).lower().startswith(root_norm.lower() + "/"):
        out.append(_norm(target)[len(root_norm) + 1:])
    return out


def match_kind(literal, target, root=None):
    """How a literal spells the target, or None."""
    lit = _norm(literal)
    if not lit:
        return None
    base = os.path.basename(_norm(target))
    for sp in spellings(target, root):
        if lit == sp or lit.lower() == sp.lower():
            return M_EXACT
    if lit.lower().endswith("/" + base.lower()):
        return M_TAIL
    if lit.lower() == base.lower():
        return M_BASENAME
    return None


# ------------------------------------------------------------------ site extraction


def _const_strs(node):
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def _assignments(tree):
    """{name: [literals]} for ``NAME = <expression built from literals and other names>``.

    Names are resolved transitively (up to NAME_HOPS rounds) because a path is usually composed in
    two steps: ``p = os.path.join(HERE, 'lane', NAME)`` and then ``open(p)``.  One hop published the
    composer's own literals ('lane') and lost the file name (E470 first draft).
    """
    raw = {}
    for node in ast.walk(tree):
        targets = []
        value = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if not targets or value is None:
            continue
        lits = _const_strs(value)
        names = [n.id for n in ast.walk(value) if isinstance(n, ast.Name)]
        for t in targets:
            if isinstance(t, ast.Name):
                slot = raw.setdefault(t.id, {"lits": [], "names": []})
                slot["lits"].extend(lits)
                slot["names"].extend(names)
    out = {k: list(v["lits"]) for k, v in raw.items()}
    for _ in range(NAME_HOPS):
        grew = False
        for name, slot in raw.items():
            for other in slot["names"]:
                if other == name:
                    continue
                extra = [x for x in out.get(other, []) if x not in out[name]]
                if extra:
                    out[name].extend(extra)
                    grew = True
        if not grew:
            break
    return out


def _is_opener(call):
    f = call.func
    if isinstance(f, ast.Name) and f.id in OPEN_FUNCS:
        return True
    if isinstance(f, ast.Attribute) and f.attr in OPEN_ATTRS:
        return True
    return False


def _is_glob(call):
    f = call.func
    if isinstance(f, ast.Name) and f.id in GLOB_FUNCS:
        return True
    if isinstance(f, ast.Attribute) and f.attr in GLOB_FUNCS:
        return True
    return False


def _evidence(call, assigned):
    """Literals the call could use as a path: its own literals plus one hop through names."""
    lits = list(_const_strs(call))
    for node in ast.walk(call):
        if isinstance(node, ast.Name) and node.id in assigned:
            lits.extend(assigned[node.id])
    return lits


def sites_for(pop, root=None):
    """{target: {"openers": [...], "globs": [...]}} plus the site-side tallies."""
    root = root or ROOT
    by_lit = {}
    for rec in pop:
        by_lit.setdefault(os.path.basename(rec["basename"]).lower(), []).append(rec["target"])
    found = {rec["target"]: {"openers": [], "globs": []} for rec in pop}
    scanned = 0
    for rel in e468._walk_py(root):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        if not any(b in text.lower() for b in by_lit):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        scanned += 1
        assigned = _assignments(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _is_opener(node):
                for lit in _evidence(node, assigned):
                    for tgt in by_lit.get(os.path.basename(_norm(lit)).lower(), []):
                        kind = match_kind(lit, tgt, root)
                        if kind is None:
                            continue
                        found[tgt]["openers"].append({
                            "source": rel, "line": getattr(node, "lineno", 0),
                            "literal": lit, "match": kind,
                        })
                        break
            elif _is_glob(node):
                for lit in _evidence(node, assigned):
                    if not lit:
                        continue
                    pat = _norm(lit)
                    if not any(ch in pat for ch in "*?["):
                        continue
                    if not literal_segments(pat):
                        # a bare "*" says nothing about which file it lands on; fnmatch's "*"
                        # spans separators and would "match" every target (E273's glob('*') did
                        # exactly that for 24 of 24).  An unbounded sweep carries no information.
                        continue
                    cands = []
                    if not os.path.isabs(pat):
                        cands.append(pat)
                        cands.append(_norm(os.path.join(os.path.dirname(rel), pat)))
                    else:
                        cands.append(pat)
                    for tgt_rec in pop:
                        best = None
                        for sp in spellings(tgt_rec["target"], root):
                            for cand in cands:
                                score = glob_score(sp, cand)
                                if score is not None and (best is None or score > best[1]):
                                    best = (cand, score)
                        if best is None:
                            continue
                        found[tgt_rec["target"]]["globs"].append({
                            "source": rel, "line": getattr(node, "lineno", 0),
                            "pattern": lit, "resolved_as": best[0],
                            "literal_segments": best[1],
                        })
    for tgt in found:
        for key in ("openers", "globs"):
            seen, uniq = set(), []
            for s in found[tgt][key]:
                sig = (s["source"], s["line"], s.get("literal") or s.get("pattern"))
                if sig in seen:
                    continue
                seen.add(sig)
                uniq.append(s)
            uniq.sort(key=lambda s: (s["source"], s["line"]))
            found[tgt][key] = uniq
    return found, {"sources_scanned_with_a_candidate": scanned, "distinct_basenames": len(by_lit)}


def literal_segments(pattern):
    """Segments of a glob pattern that carry no wildcard (the only part that constrains it)."""
    return [s for s in _norm(pattern).split("/")
            if s and not any(ch in s for ch in "*?[")]


def glob_score(target, pattern):
    """None when the pattern cannot land on the target; else the number of literal segments.

    Matching is per segment (``*`` and ``?`` stay inside one segment, ``**`` spans segments) --
    the rule Python's glob/pathlib use, not fnmatch's, whose ``*`` also swallows separators.  A
    pattern with no literal segment is an unbounded sweep and is refused by the caller.
    """
    import fnmatch
    pat = [s for s in _norm(pattern).split("/") if s]
    tgt = [s for s in _norm(target).split("/") if s]
    n = _seg_match(pat, tgt, fnmatch)
    return None if n is None else len(literal_segments(pattern))


def _seg_match(pat, tgt, fnmatch):
    if not pat:
        return 0 if not tgt else None
    head, rest = pat[0], pat[1:]
    if head == "**":
        best = None
        for i in range(len(tgt) + 1):
            sub = _seg_match(rest, tgt[i:], fnmatch)
            if sub is not None and (best is None or sub > best):
                best = sub
        return best
    if not tgt:
        return None
    if not fnmatch.fnmatchcase(tgt[0].lower(), head.lower()):
        return None
    return _seg_match(rest, tgt[1:], fnmatch)


def key_reads(pop, root=None):
    """Sites in modules that open the pointing face AND carry the pointer key literal."""
    root = root or ROOT
    faces = {}
    for rec in pop:
        for p in rec["pointers"]:
            faces.setdefault(_norm(p["face"]), set()).add(p["key"])
    out = []
    for rel in e468._walk_py(root):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        hits = [f for f in faces if os.path.basename(f) in text]
        if not hits:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        assigned = _assignments(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _is_opener(node):
                continue
            ev = [_norm(x) for x in _evidence(node, assigned)]
            for face in hits:
                if not any(ev_lit == face or ev_lit.endswith("/" + os.path.basename(face))
                           for ev_lit in ev):
                    continue
                keys = sorted(k for k in faces[face] if k in text)
                for key in keys:
                    out.append({"source": rel, "line": getattr(node, "lineno", 0),
                                "face": face, "key": key})
    out.sort(key=lambda s: (s["source"], s["line"], s["face"]))
    return out


# ------------------------------------------------------------------ classification


def _is_smoke(rel):
    return os.path.basename(rel).startswith(("smoke_test.py", "run_e"))


def _is_round_script(rel):
    return os.path.basename(rel).startswith("_")


def residue_of(sites, producers):
    """Which family opens the target, most-proving first."""
    openers = sites.get("openers") or []
    globs = sites.get("globs") or []
    if openers:
        outsiders = [s for s in openers
                     if s["source"] not in producers and not _is_smoke(s["source"])
                     and not _is_round_script(s["source"])]
        if outsiders:
            return R_OTHER
        short = [s for s in openers if s["source"] not in producers]
        if not short:
            return R_PRODUCER
        if all(_is_smoke(s["source"]) for s in short):
            return R_SMOKE
        if all(_is_round_script(s["source"]) for s in short):
            return R_ROUND
        return R_PRODUCER
    if globs:
        return R_GLOB
    return R_NEVER


def verdict_for(summary):
    n = summary["distinct_targets"]
    if n == 0:
        return V_EMPTY
    by = summary["residue_classes"]
    if by.get(R_OTHER):
        return V_SOME_OTHER
    if by.get(R_GLOB):
        return V_SOME_GLOB
    if by.get(R_NEVER):
        return V_SOME_NEVER
    return V_ALL_PRODUCER


# ------------------------------------------------------------------ build


def build(write=True, root=None):
    root = root or ROOT
    pop, meta = population(root)
    sites, site_meta = sites_for(pop, root)
    producers = e468.producer_map(root)
    keyread = key_reads(pop, root)

    rows = []
    for rec in pop:
        tgt = rec["target"]
        # the writer map is keyed by e464.face_stem (dates and separators stripped), so the target
        # and the pointing face must be looked up through that same rule and not through the raw
        # file stem -- a raw stem never matches and every writer looked like an unrelated study.
        stem = e464.face_stem(os.path.basename(tgt))
        writers = sorted(producers.get(stem, []))
        face_writers = []
        for p in rec["pointers"]:
            for src in producers.get(e464.face_stem(os.path.basename(p["face"])), []):
                face_writers.append(src)
        producers_here = sorted(set(writers) | set(face_writers))
        mine = sites.get(tgt, {"openers": [], "globs": []})
        rows.append({
            "target": tgt,
            "basename": rec["basename"],
            "pointers": rec["pointers"],
            "producers_of_the_target": writers,
            "producers_of_the_pointing_face": sorted(set(face_writers)),
            "target_exists_on_disk": os.path.isfile(os.path.join(root, tgt)),
            "openers": mine["openers"],
            "globs": mine["globs"],
            "key_read_sites": [k for k in keyread if k["face"] == _norm(rec["pointers"][0]["face"])]
            if rec["pointers"] else [],
            "residue": residue_of(mine, producers_here),
        })

    by_residue, by_match = {}, {}
    for r in rows:
        by_residue[r["residue"]] = by_residue.get(r["residue"], 0) + 1
        for s in r["openers"]:
            by_match[s["match"]] = by_match.get(s["match"], 0) + 1

    summary = {
        "card": CARD,
        "source_face_pointers": meta["source_face_pointers"],
        "source_face_verdict": meta["source_face_verdict"],
        "distinct_targets": len(rows),
        "targets_that_exist_on_disk": sum(1 for r in rows if r["target_exists_on_disk"]),
        "targets_with_an_opener": sum(1 for r in rows if r["openers"]),
        "targets_with_only_a_glob": sum(1 for r in rows if not r["openers"] and r["globs"]),
        "targets_with_no_site_at_all": sum(1 for r in rows if not r["openers"] and not r["globs"]),
        "opener_sites_total": sum(len(r["openers"]) for r in rows),
        "opener_sites_by_match": by_match,
        "glob_sites_total": sum(len(r["globs"]) for r in rows),
        "pointer_key_read_sites": len(keyread),
        "targets_with_a_pointer_key_read": sum(1 for r in rows if r["key_read_sites"]),
        "residue_classes": by_residue,
        "sources_scanned_with_a_candidate": site_meta["sources_scanned_with_a_candidate"],
    }
    face = {
        "card": CARD,
        "study": "E470_target_read",
        "title": "a pointer the repo root cannot follow usually names a file no site ever opens",
        "evidence_cutoff": _today(),
        "population_source": "results/state_tilt/pointerreach_latest.json (E468 rows, re-read)",
        "verdict": verdict_for(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "match_kinds": list(MATCH_KINDS),
        "residue_classes": list(RESIDUES),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "an opener is a call named open / io.open / Path.read_text / json.load / yaml.load / "
            "pandas.read_* / gzip.open; a reader that opens the path elsewhere (a subprocess, a "
            "shell redirect, the console app) is not in the population",
            "path evidence is the literals in the call plus one hop through names assigned a "
            "literal in the same module; a path composed from two separate names is published as "
            "basename-only (the base is not proven), not as a read of this target",
            "a basename match proves a file of that name is opened, not that it is THIS file; the "
            "three match kinds are published apart for that reason",
            "glob patterns are matched per segment ('*' inside one segment, '**' across "
            "segments) -- the glob/pathlib rule; a pattern with no literal segment is an unbounded "
            "sweep and is published as no match (an fnmatch '*' would have matched every target, "
            "which is how the first draft read 24 of 24 as glob-reached)",
            "a pointer-key read site shows a module that opens the pointing face and carries the "
            "key literal; whether the value flows into an opener is not followed (no dataflow)",
            "own outputs (e461..e470 and their runners) are excluded so the census cannot count "
            "itself",
        ],
    }
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False)
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, _today()))
        for p in (dated, os.path.join(OUTDIR, FACE_NAME)):
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(payload + "\n")
        return face, [dated, os.path.join(OUTDIR, FACE_NAME)]
    return face, []


# ------------------------------------------------------------------ checks


def _recompute_tallies(face):
    rows = face["rows"]
    by_residue = {}
    for r in rows:
        by_residue[r["residue"]] = by_residue.get(r["residue"], 0) + 1
    return {
        "distinct_targets": len(rows),
        "targets_with_an_opener": sum(1 for r in rows if r["openers"]),
        "opener_sites_total": sum(len(r["openers"]) for r in rows),
        "glob_sites_total": sum(len(r["globs"]) for r in rows),
        "residue_classes": by_residue,
        "verdict": verdict_for(face["summary"]),
    }


def row_problems(face):
    """Every row's residue re-derived from its own sites (not from its own label)."""
    bad = []
    for row in face.get("rows") or []:
        producers = sorted(set(row.get("producers_of_the_target") or [])
                           | set(row.get("producers_of_the_pointing_face") or []))
        want = residue_of({"openers": row.get("openers") or [], "globs": row.get("globs") or []},
                          producers)
        if want != row.get("residue"):
            bad.append("%s: published residue %r, its sites say %r"
                       % (row.get("target"), row.get("residue"), want))
        for s in row.get("openers") or []:
            if s.get("match") not in MATCH_KINDS:
                bad.append("%s: opener match outside the vocabulary: %r"
                           % (row.get("target"), s.get("match")))
    return bad


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    got = _recompute_tallies(face)
    problems = list(row_problems(face))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary: %r" % (face.get("verdict"),))
    for cls in (face["summary"].get("residue_classes") or {}):
        if cls not in RESIDUES:
            problems.append("residue class outside the frozen vocabulary: %r" % (cls,))
    for key in ("distinct_targets", "targets_with_an_opener", "opener_sites_total",
                "glob_sites_total", "residue_classes"):
        if got[key] != face["summary"][key]:
            problems.append("%s: %r != %r" % (key, got[key], face["summary"][key]))
    if got["verdict"] != face["verdict"]:
        problems.append("verdict: %s != %s" % (got["verdict"], face["verdict"]))
    print(json.dumps({"problems": problems, "tallies": got}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify():
    face, _ = build(write=False)
    on_disk = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = []
    for key in ("distinct_targets", "targets_with_an_opener", "opener_sites_total",
                "glob_sites_total", "residue_classes", "verdict", "opener_sites_by_match"):
        if face["summary"].get(key) != on_disk["summary"].get(key):
            problems.append("%s: fresh %r != published %r"
                            % (key, face["summary"].get(key), on_disk["summary"].get(key)))
    print(json.dumps({"problems": problems,
                      "fresh": face["summary"]["distinct_targets"],
                      "published": on_disk["summary"]["distinct_targets"]},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(tmp):
    os.makedirs(os.path.join(tmp, "results", "state_tilt"))
    os.makedirs(os.path.join(tmp, "results", "lane"))
    os.makedirs(os.path.join(tmp, "scripts"))
    # the pointing face E468 would have published (bare filename, resolves from its own directory)
    json.dump({"source_face": "SIBLING-2026-11-01.json"},
              io.open(os.path.join(tmp, "results", "lane", "up.json"), "w", encoding="utf-8"))
    json.dump({"ok": True},
              io.open(os.path.join(tmp, "results", "lane", "SIBLING-2026-11-01.json"), "w",
                      encoding="utf-8"))
    json.dump({"rows": [{"face": "results/lane/up.json", "key": "source_face",
                         "value": "SIBLING-2026-11-01.json",
                         "spelling": "bare_filename_no_directory",
                         "required_base": e466.B_OWN,
                         "target": "results/lane/SIBLING-2026-11-01.json",
                         "basename": "SIBLING-2026-11-01.json"}]},
              io.open(os.path.join(tmp, "results", "state_tilt", "pointerreach_latest.json"), "w",
                      encoding="utf-8"))
    # the writer of the target: composes the path from its own directory
    io.open(os.path.join(tmp, "scripts", "prod_sibling.py"), "w", encoding="utf-8").write(
        "import os, json\n"
        "HERE = os.path.dirname(os.path.abspath(__file__))\n"
        "NAME = 'SIBLING-2026-11-01.json'\n"
        "def build():\n"
        "    p = os.path.join(HERE, '..', 'results', 'lane', NAME)\n"
        "    json.dump({}, open(p, 'w'))\n")
    return tmp


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": str(detail)[:200]})

    leg("an exact literal is exact",
        match_kind("results/lane/x.json", "results/lane/x.json") == M_EXACT)
    leg("a composed tail is a tail",
        match_kind("lane/x.json", "results/lane/x.json") == M_TAIL)
    leg("a bare basename is only a basename",
        match_kind("x.json", "results/lane/x.json") == M_BASENAME)
    leg("an unrelated literal does not match",
        match_kind("results/lane/y.json", "results/lane/x.json") is None)
    leg("an absolute spelling of the same file matches as exact",
        match_kind("C:/repo/results/lane/x.json", "C:/repo/results/lane/x.json") == M_EXACT)
    leg("never opened is its own class", residue_of({"openers": [], "globs": []}, []) == R_NEVER)
    leg("a glob-only target is its own class",
        residue_of({"openers": [], "globs": [{"source": "a.py", "line": 1}]}, []) == R_GLOB)
    leg("the writer alone is the producer class",
        residue_of({"openers": [{"source": "scripts/prod.py", "line": 1, "match": M_BASENAME}]},
                   ["scripts/prod.py"]) == R_PRODUCER)
    leg("an outside opener is the other class",
        residue_of({"openers": [{"source": "scripts/study.py", "line": 1, "match": M_BASENAME}]},
                   ["scripts/prod.py"]) == R_OTHER)
    leg("a smoke leg alone is its own class",
        residue_of({"openers": [{"source": "scripts/run_e1_smoke_leg.py", "line": 1,
                                 "match": M_EXACT}]}, []) == R_SMOKE)
    leg("a one-off round script alone is its own class",
        residue_of({"openers": [{"source": "scripts/_r1.py", "line": 1, "match": M_EXACT}]},
                   []) == R_ROUND)
    leg("a bare '*' does not land on anything",
        glob_score("results/state_tilt/x.json", "*") is None)
    leg("a directory prefix is a glob with one literal segment",
        glob_score("results/state_tilt/x.json", "results/**/*.json") == 1,
        glob_score("results/state_tilt/x.json", "results/**/*.json"))
    leg("a one-segment '*' pattern cannot reach a nested file",
        glob_score("results/state_tilt/x.json", "*.json") is None)
    leg("* stays inside one segment (the glob rule, not fnmatch's)",
        glob_score("results/state_tilt/x.json", "results/*") is None)
    leg("** spans segments",
        glob_score("results/state_tilt/x.json", "results/**") == 1)
    leg("a literal segment must still match",
        glob_score("results/state_tilt/x.json", "docs/**/*.json") is None)

    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        pop, meta = population(tmp)
        leg("population reads the E468 face", len(pop) == 1 and meta["source_face_pointers"] == 1,
            pop)
        sites, _ = sites_for(pop, tmp)
        tgt = "results/lane/SIBLING-2026-11-01.json"
        found = sites[tgt]["openers"]
        leg("the writer's open() is found through the assigned NAME", len(found) >= 1, found)
        leg("its evidence is the basename, not the whole path",
            found and found[0]["match"] in (M_BASENAME, M_TAIL), found)
        prod = e468.producer_map(tmp)
        leg("producer map ties the target to its writer",
            "scripts/prod_sibling.py" in prod.get(e464.face_stem("SIBLING-2026-11-01.json"), []),
            prod)
        face, _ = build(write=False, root=tmp)
        leg("a target opened only by its writer is classed as producer",
            face["rows"][0]["residue"] == R_PRODUCER, face["rows"][0]["residue"])
        tallies = _recompute_tallies(face)
        leg("tallies re-derive from the rows",
            tallies["distinct_targets"] == len(face["rows"])
            and tallies["verdict"] == face["verdict"])
        again, _ = build(write=False, root=tmp)
        leg("build is deterministic",
            json.dumps(face, sort_keys=True) == json.dumps(again, sort_keys=True))
        doctored = json.loads(json.dumps(face))
        doctored["rows"][0]["residue"] = R_OTHER
        leg("a wrong residue label is caught", row_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["rows"][0]["openers"][0]["match"] = "whatever"
        leg("a match outside the vocabulary is caught", row_problems(doctored2) != [])

    bad = [l for l in legs if not l["ok"]]
    print(json.dumps({"legs": legs, "passed": len(legs) - len(bad), "failed": len(bad)},
                     ensure_ascii=False, indent=1))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face, paths = build(write=True)
        print(json.dumps({"wrote": paths, "summary": face["summary"], "verdict": face["verdict"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))