"""E492 -- of the multi-composed ``*_latest.json`` names, how many extra composers are
doctor harnesses, and does any of them leave a mutated face behind?

E491 (r1516) published 176 latest names with a static composer; 51 of them have two or
more composers.  A sample of the extras is leg runners (``scripts/run_eXXX_smoke_leg.py``)
that copy a face, mutate a published count, run the leg, and put the original back.  Two
things follow that E491 never measured:

  * if BOTH composers of a name are harnesses, the harness is the only writer the scan can
    see -- the real producer is invisible, so "several composers" is not "several producers";
  * a harness that writes the published path has to restore it, and a harness that writes
    once leaves whatever it wrote.

Measured, whole-repo, statically plus one live arm, no draws and no engine:

  1. take E491's multi-composed rows verbatim (never re-derived from prose);
  2. label each composer by its source: producer / doctor harness / one-off ``_rNNN`` repair;
  3. per composer, count its own write sites into that name and whether it saves the
     original away first (a copy call whose SOURCE is the latest name);
  4. live arm: for each multi-composed name, does the file on disk exist and parse as JSON
     right now, and are there leftover mutant artefacts (``*_mut*``, ``*.bak``, doctored)
     sitting in the published directory.

Reads scripts/, Tools/ and firm/ Python sources; writes
results/state_tilt/LATESTDOCTOR-<cutoff>.json plus latestdoctor_latest.json.
"""
import argparse
import ast
import glob
import io
import json
import os
import re
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402
import e489_write_wire as e489  # noqa: E402
import e491_latest_copier as e491  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "latestdoctor_latest.json"
DATED_PREFIX = "LATESTDOCTOR"
CARD = ("E492-OF-THE-MULTI-COMPOSED-LATEST-NAMES-HOW-MANY-EXTRA-COMPOSERS-ARE-DOCTOR-"
        "HARNESSES-AND-DO-ANY-OF-THEM-LEAVE-A-MUTATED-FACE-BEHIND")
LATEST_SUFFIX = "_latest.json"
SELF_EXCLUDED = ("e492_", "run_e492")

R_PRODUCER = "a_producer"
R_HARNESS = "a_doctor_harness"
R_ONEOFF = "a_one_off_repair"
ROLES = (R_PRODUCER, R_HARNESS, R_ONEOFF)

HARNESS_RE = re.compile(r"(^run_e\d+)|(smoke_leg)|(doctor)|(mutat)")
ONEOFF_RE = re.compile(r"^_r\d+")
MUTANT_RE = re.compile(r"(_mut|_bak|\.bak|doctored|corrupt|\.tmp)", re.IGNORECASE)

D_MUTATES_THEN_RESTORES = "writes_the_name_twice_so_it_can_put_the_original_back"
D_SINGLE_WRITE = "writes_the_name_once_with_no_restore_in_the_same_source"

V_EMPTY = "no_latest_face_has_several_composers"
V_NO_HARNESS = "no_multi_composed_face_has_a_doctor_harness_among_its_composers"
V_MIXED = "a_minority_of_the_extra_composers_are_doctor_harnesses"
V_ALL = "every_extra_composer_of_a_multi_composed_face_is_a_doctor_harness"
V_LEFTOVER = "at_least_one_multi_composed_face_is_left_behind_in_a_mutated_state"
VERDICT_VOCAB = (V_EMPTY, V_NO_HARNESS, V_MIXED, V_ALL, V_LEFTOVER)

COPY_ATTRS = ("copyfile", "copy", "copy2", "move", "rename", "replace")


def role_of(source):
    base = os.path.basename(source).lower()
    if HARNESS_RE.search(base):
        return R_HARNESS
    if ONEOFF_RE.search(base):
        return R_ONEOFF
    return R_PRODUCER


READ_ATTRS = ("read", "read_text", "read_bytes", "load", "loads", "load_sql")
WRITE_ATTRS = ("write", "write_text", "write_bytes", "dump", "dump_json", "write_json")
WRITE_MODES = ("w", "wb", "a", "ab", "x", "xb", "r+", "rb+", "w+", "a+")


def _mode_of_call(node):
    """'write' / 'read' / None for one call node."""
    func = node.func
    if isinstance(func, ast.Attribute):
        if func.attr in WRITE_ATTRS or func.attr in COPY_ATTRS:
            return "write"
        if func.attr in READ_ATTRS:
            return "read"
        if func.attr in ("open",):
            return _open_mode(node)
        return None
    if isinstance(func, ast.Name):
        if func.id in ("open", "write_json", "dump_json"):
            return _open_mode(node) if func.id == "open" else "write"
        if func.id in ("load_json", "read_json"):
            return "read"
    return None


def _open_mode(node):
    if len(node.args) < 2:
        return "read"
    arg = node.args[1]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return "write" if arg.value in WRITE_MODES else "read"
    return None


_FOLDER_CACHE = {}


class LineIndex(object):
    """Bindings per line, built once per source.

    ``Folder.function_bindings`` and ``FolderEx.for_bindings`` each walk the whole tree, so
    calling them per call node is quadratic: the first build of this study stalled for
    minutes in ``ast.walk`` and had to be killed.  This index walks the tree twice in total.
    """

    def __init__(self, folder):
        self.folder = folder
        self.module = folder.module_bindings
        tree = folder.tree
        self.funcs = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            local = {}
            for sub in ast.walk(node):
                folder._bind(sub, local)
            self.funcs.append((getattr(node, "lineno", 0),
                               getattr(node, "end_lineno", 0) or getattr(node, "lineno", 0),
                               local))
        self.loops = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.For):
                continue
            start = getattr(node, "lineno", 0)
            end = getattr(node, "end_lineno", start) or start
            targets = []
            if isinstance(node.target, ast.Name):
                targets = [node.target.id]
            elif isinstance(node.target, (ast.Tuple, ast.List)):
                targets = [t.id for t in node.target.elts if isinstance(t, ast.Name)]
            binding = {}
            for name in targets:
                binding.setdefault(name, node.iter)
            if binding:
                self.loops.append((start, end, binding))
        self.calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]

    def names_at(self, line):
        out = dict(self.module)
        best = None
        for start, end, local in self.funcs:
            if start <= line <= end and (best is None or start > best[0]):
                best = (start, end, local)
        if best is not None:
            out.update(best[2])
        for start, end, binding in self.loops:
            if start <= line <= end:
                for name, value in binding.items():
                    out.setdefault(name, value)
        return out


def _folder_for(rel, text, root):
    """One parse, one folder and one line index per source."""
    key = (rel, len(text), text[:64], text[-64:])
    got = _FOLDER_CACHE.get(key)
    if got is not None:
        return got
    tree = ast.parse(text)
    folder = e489.FolderEx(rel, tree, root)
    index = LineIndex(folder)
    _FOLDER_CACHE[key] = (tree, folder, index)
    return tree, folder, index


def named_sites(rel, text, root, name):
    """Every call in ``rel`` that names the latest file, split read / write.

    E491's census cannot tell ``open(path)`` from ``open(path, 'w')``, so a harness that
    reads a face before mutating it looks like an extra writer.  This split keeps that
    apart and publishes both numbers.
    """
    root = root or ROOT
    try:
        tree, folder, index = _folder_for(rel, text, root)
    except SyntaxError:
        return [], "the_source_cannot_be_parsed"
    sites = []
    for node in index.calls:
        if not isinstance(node, ast.Call):
            continue
        line = getattr(node, "lineno", 0)
        positions = []
        if isinstance(node.func, ast.Attribute) and node.func.attr in COPY_ATTRS \
                and len(node.args) >= 2:
            positions = [(node.args[0], "read"), (node.args[1], "write")]
        else:
            kind = _mode_of_call(node)
            if kind is None or not node.args:
                continue
            positions = [(node.args[0], kind)]
            if isinstance(node.func, ast.Name) and node.func.id == "open" and len(node.args) > 1:
                positions.append((node.args[1], None))
        if not positions:
            continue
        names = index.names_at(line)
        for arg, kind in positions:
            if kind is None:
                continue
            paths, unfolded = folder.fold(arg, names, 0)
            paths = [p for p in (e491._clean(x) for x in paths) if p]
            if name not in [os.path.basename(p) for p in paths]:
                continue
            sites.append({"source": rel, "line": line, "mode": kind,
                          "callee": (node.func.id if isinstance(node.func, ast.Name)
                                     else node.func.attr),
                          "paths": paths[:e491.MAX_PATHS],
                          "unfolded": bool(unfolded)})
    sites.sort(key=lambda s: (s["line"], s["mode"]))
    return sites, None


def scan_sources(root=None):
    """E491's scan minus this study's own files."""
    root = root or ROOT
    return [(rel, text) for rel, text in e491.scan_sources(root)
            if not os.path.basename(rel).startswith(SELF_EXCLUDED)]


def backup_saves(rel, text, root=None):
    """Copy calls that move a latest name OUT to a non-latest destination."""
    root = root or ROOT
    try:
        tree, folder, index = _folder_for(rel, text, root)
    except SyntaxError:
        return []
    out = []
    for node in index.calls:
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in COPY_ATTRS or len(node.args) < 2:
            continue
        line = getattr(node, "lineno", 0)
        names = index.names_at(line)
        src, _ = folder.fold(node.args[0], names, 0)
        dst, _ = folder.fold(node.args[1], names, 0)
        src = [p for p in (e491._clean(x) for x in src) if p]
        dst = [p for p in (e491._clean(x) for x in dst) if p]
        if not any(os.path.basename(p).endswith(LATEST_SUFFIX) for p in src):
            continue
        if any(os.path.basename(p).endswith(LATEST_SUFFIX) for p in dst):
            continue
        out.append({"source": rel, "line": line, "callee": node.func.attr,
                    "source_paths": src[:e491.MAX_PATHS],
                    "destination_paths": dst[:e491.MAX_PATHS]})
    return out


def _site_cache(root):
    cache = {}
    for rel, text in scan_sources(root):
        sites, note = e491.composers_in(rel, text, root)
        cache[rel] = {"sites": sites, "text": text, "note": note,
                      "saves": backup_saves(rel, text, root)}
    return cache


def _writes_named(sites, name):
    hits = []
    for site in sites:
        if name in [os.path.basename(p) for p in site.get("destination_paths") or []]:
            hits.append(site)
    return hits


def _published_path(composers, name, root):
    for cand in composers:
        for path in cand.get("destination_paths") or []:
            if os.path.basename(path) == name and os.path.exists(os.path.join(root, path)):
                return path
    for cand in composers:
        for path in cand.get("destination_paths") or []:
            if os.path.basename(path) == name:
                return path
    return "results/state_tilt/" + name


def _reads_json(path):
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            json.load(fh)
        return True
    except (OSError, ValueError, UnicodeError):
        return False


def leftover_mutants(root=None):
    root = root or ROOT
    base = os.path.join(root, "results", "state_tilt")
    found = []
    if not os.path.isdir(base):
        return found
    for name in sorted(os.listdir(base)):
        if not MUTANT_RE.search(name):
            continue
        found.append({"name": name,
                      "bytes": os.path.getsize(os.path.join(base, name))})
    return found


def population(root=None):
    root = root or ROOT
    e491_rows, meta491 = e491.population(root)
    multi = [r for r in e491_rows if r.get("compose_class") == e491.C_SEVERAL]
    self_names = (FACE_NAME, DATED_PREFIX.lower() + "-")
    dropped_self = [r["latest_basename"] for r in multi
                    if r["latest_basename"] == FACE_NAME
                    or r["latest_basename"].startswith(self_names[1])]
    multi = [r for r in multi if r["latest_basename"] not in dropped_self]
    cache = _site_cache(root)
    out = []
    for row in multi:
        name = row["latest_basename"]
        composers = []
        for cand in row["composers"]:
            src = cand["source"]
            entry = cache.get(src) or {"sites": [], "text": "", "saves": [], "note": None}
            writes = _writes_named(entry["sites"], name)
            named, _note = named_sites(src, entry["text"], root, name) if entry["text"] else ([], None)
            w_sites = [s for s in named if s["mode"] == "write"]
            r_sites = [s for s in named if s["mode"] == "read"]
            lines = sorted({int(w.get("line") or 0) for w in w_sites})
            cand_lines = sorted({int(w.get("line") or 0) for w in writes})
            composers.append({
                "source": src,
                "line": cand.get("line"),
                "kind": cand.get("kind"),
                "callee": cand.get("callee"),
                "role": role_of(src),
                "destination_paths": cand.get("destination_paths") or [],
                "writes_this_name_at_lines": lines,
                "write_site_count": len(lines),
                "read_site_count": len({int(r.get("line") or 0) for r in r_sites}),
                "named_sites_without_a_mode": max(0, len(cand_lines) - len(lines)),
                "reads_the_name_before_it_writes_it": bool(
                    r_sites and lines and min(int(r.get("line") or 0) for r in r_sites)
                    < min(lines)),
                "saves_the_original_away_first": bool(
                    r_sites and len(lines) >= 2),
                "restore_call_lines": lines[1:] if len(lines) >= 2 else [],
                "mutation_discipline": (D_MUTATES_THEN_RESTORES if len(lines) >= 2
                                        else D_SINGLE_WRITE),
            })
        composers.sort(key=lambda c: (c["source"], int(c["line"] or 0)))
        by_source = {}
        for c in composers:
            by_source.setdefault(c["source"], []).append(c)
        producers = sorted(s for s, cs in by_source.items()
                           if any(c["role"] == R_PRODUCER for c in cs))
        primary_source = producers[0] if producers else sorted(by_source)[0]
        extras = []
        for src in sorted(by_source):
            if src == primary_source:
                continue
            sites = by_source[src]
            lines = sorted({ln for c in sites for ln in c["writes_this_name_at_lines"]})
            extras.append({
                "source": src,
                "role": sites[0]["role"],
                "site_lines": [c["line"] for c in sites],
                "write_site_count": len(lines),
                "reads_the_name_before_it_writes_it": any(
                    c["reads_the_name_before_it_writes_it"] for c in sites),
                "saves_the_original_away_first": any(
                    c["saves_the_original_away_first"] for c in sites),
                "mutation_discipline": (D_MUTATES_THEN_RESTORES if len(lines) >= 2
                                        else D_SINGLE_WRITE),
            })
        published = _published_path(composers, name, root)
        path_on_disk = os.path.join(root, published)
        exists = os.path.exists(path_on_disk)
        out.append({
            "latest_basename": name,
            "published_path": published,
            "composer_count": len(composers),
            "composer_sources": sorted(by_source),
            "composers": composers,
            "primary_composer_source": primary_source,
            "extra_composer_count": len(extras),
            "extras": extras,
            "extra_roles": sorted({e["role"] for e in extras}),
            "extras_are_all_harnesses": bool(extras) and all(
                e["role"] == R_HARNESS for e in extras),
            "has_a_producer_composer": bool(producers),
            "harness_composer_count": sum(1 for c in composers if c["role"] == R_HARNESS),
            "harness_writes_the_published_path": any(
                c["role"] == R_HARNESS and os.path.basename(c["destination_paths"][0]) == name
                for c in composers if c.get("destination_paths")),
            "harness_single_write_composers": len(
                [e for e in extras if e["role"] == R_HARNESS
                 and e["mutation_discipline"] == D_SINGLE_WRITE]),
            "extra_sites_without_a_restore": len(
                [e for e in extras if e["mutation_discipline"] == D_SINGLE_WRITE]),
            "exists_on_disk": exists,
            "parses_as_json": _reads_json(path_on_disk) if exists else None,
        })
    leftovers = leftover_mutants(root)
    meta = {
        "scan_directories": list(e491.SCAN_DIRS),
        "sources_scanned": len(scan_sources(root)),
        "excluded_source_prefixes": list(e491.SELF_EXCLUDED) + list(SELF_EXCLUDED),
        "self_faces_excluded": sorted(dropped_self),
        "self_exclusion_note": "this study writes latestdoctor_latest.json itself; its "
                               "own producer is excluded from the scan, so leaving the name "
                               "in would have published a face whose only visible composer "
                               "is a harness -- a self-inclusion artefact, not a finding",
        "e491_population_available": len(e491_rows),
        "e491_population_accounted_for": meta491.get("sources_mentioning_a_latest_name"),
        "population_definition": "E491's rows whose compose_class is "
                                 "'%s'" % e491.C_SEVERAL,
        "role_rule": {
            R_HARNESS: "source basename matches %s" % HARNESS_RE.pattern,
            R_ONEOFF: "source basename matches %s" % ONEOFF_RE.pattern,
            R_PRODUCER: "everything else in the scanned sources",
        },
        "live_arm": "each published path is opened and parsed as JSON at build time; "
                    "leftover mutant artefacts are listed from results/state_tilt",
    }
    return out, leftovers, meta


def _extra_sources_of_role(row, role):
    return [(row.get("latest_basename"), e["source"])
            for e in (row.get("extras") or []) if e.get("role") == role]


def _recompute(face):
    rows = face.get("rows") or []
    leftovers = face.get("leftover_mutant_files") or []
    sites = [(c["source"], int(c.get("line") or 0)) for r in rows
             for c in (r.get("composers") or [])]
    extras = [(e["source"], int(r.get("index") or 0)) for r in rows
              for e in (r.get("extras") or [])]
    extra_harness = [k for r in rows for k in _extra_sources_of_role(r, R_HARNESS)]
    extra_oneoff = [k for r in rows for k in _extra_sources_of_role(r, R_ONEOFF)]
    extra_producer = [k for r in rows for k in _extra_sources_of_role(r, R_PRODUCER)]
    by_role = {k: 0 for k in ROLES}
    for r in rows:
        for c in r.get("composers") or []:
            if c.get("role") in by_role:
                by_role[c["role"]] += 1
    return {
        "multi_composed_faces": len(rows),
        "composer_sites": len(set(sites)),
        "extra_composer_sites": len(set(extras)),
        "extra_composer_sites_by_role": {
            R_HARNESS: len(set(extra_harness)),
            R_ONEOFF: len(set(extra_oneoff)),
            R_PRODUCER: len(set(extra_producer)),
        },
        "composer_sites_by_role": by_role,
        "faces_whose_extras_are_all_harnesses": sum(
            1 for r in rows if r.get("extras_are_all_harnesses")),
        "faces_whose_composers_are_all_harnesses": sum(
            1 for r in rows if not r.get("has_a_producer_composer")),
        "faces_with_a_harness_writing_the_published_path": sum(
            1 for r in rows if r.get("harness_writes_the_published_path")),
        "faces_with_a_single_write_harness": sum(
            1 for r in rows if (r.get("harness_single_write_composers") or 0) > 0),
        "faces_existing_on_disk": sum(1 for r in rows if r.get("exists_on_disk")),
        "faces_parsing_as_json": sum(1 for r in rows if r.get("parses_as_json") is True),
        "faces_left_in_a_mutated_state": sum(
            1 for r in rows if r.get("exists_on_disk") and r.get("parses_as_json") is False),
        "leftover_mutant_files": len(leftovers),
    }


def _verdict(summary):
    total = int(summary.get("multi_composed_faces") or 0)
    if not total:
        return V_EMPTY
    if summary.get("faces_left_in_a_mutated_state"):
        return V_LEFTOVER
    harness = int((summary.get("extra_composer_sites_by_role") or {}).get(R_HARNESS) or 0)
    extras = int(summary.get("extra_composer_sites") or 0)
    if not harness:
        return V_NO_HARNESS
    if extras and harness >= extras:
        return V_ALL
    return V_MIXED


def card_answer(rows, leftovers):
    """The card's two halves, read off the rows rather than restated."""
    names_all_harness = sorted(r["latest_basename"] for r in rows
                               if not r.get("has_a_producer_composer"))
    unparseable = sorted(r["latest_basename"] for r in rows
                         if r.get("exists_on_disk") and r.get("parses_as_json") is False)
    single = sorted(r["latest_basename"] for r in rows
                    if (r.get("harness_single_write_composers") or 0) > 0)
    return {
        "extra_composer_sites_that_are_doctor_harnesses": sum(
            len(r["extras"]) for r in rows
            if r.get("extras") and all(e["role"] == R_HARNESS for e in r["extras"])),
        "faces_with_no_producer_composer": names_all_harness,
        "faces_whose_published_copy_does_not_parse": unparseable,
        "faces_with_a_harness_that_writes_once_and_never_restores": single,
        "leftover_mutant_files": [f["name"] for f in leftovers],
        "leaves_a_mutated_face_behind": bool(unparseable),
    }


def build(root=None, write=True):
    root = root or ROOT
    rows, leftovers, meta = population(root)
    summary = _recompute({"rows": rows, "leftover_mutant_files": leftovers})
    ans = card_answer(rows, leftovers)
    face = {
        "card": CARD,
        "study": "E492_who_the_extra_composers_of_a_multi_composed_latest_name_are",
        "title": "of the multi-composed latest names, how many extra composers are doctor "
                 "harnesses and does any leave a mutated face behind?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": meta,
        "role_definition": {
            R_PRODUCER: "a source that is not a leg runner and not a one-off _rNNN repair",
            R_HARNESS: "a leg runner (run_eNNN_smoke_leg.py, doctored/mutation harnesses)",
            R_ONEOFF: "a throwaway _rNNN repair script",
        },
        "discipline_definition": {
            D_MUTATES_THEN_RESTORES: "two or more write sites for the same name in one "
                                     "source, so the second can put the original back",
            D_SINGLE_WRITE: "exactly one write site: nothing in that source restores it",
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "card_answer": ans,
        "leftover_mutant_files": leftovers,
        "rows": rows,
        "method_limits": [
            "static plus a JSON parse: parses_as_json=false is evidence of a mutated face, "
            "parses_as_json=true is NOT evidence that the content is the producer's",
            "two write sites in one source says a restore is possible in that source, not "
            "that it ran or that the rest of the run finished",
            "role is a file-name rule: a harness living under another name is counted as a "
            "producer",
            "leftover_mutant_files lists names, not provenance: a *_bak file may be an "
            "intentional fixture",
            "the population is E491's static population; a name whose composers are all "
            "harnesses says the producer folded out of reach, not that it does not exist",
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


def row_problems(face):
    problems = []
    summary = face.get("summary") or {}
    derived = _recompute(face)
    for key, value in derived.items():
        if summary.get(key) != value:
            problems.append("%s: published %r, re-derives %r" % (key, summary.get(key), value))
    seen = set()
    for row in face.get("rows") or []:
        name = row.get("latest_basename")
        if not name or not name.endswith(LATEST_SUFFIX):
            problems.append("%r: not a latest name" % (name,))
            continue
        if name in seen:
            problems.append("%s: duplicated row" % name)
        seen.add(name)
        composers = row.get("composers") or []
        if len(composers) != row.get("composer_count"):
            problems.append("%s: composer_count %r but %d composers"
                            % (name, row.get("composer_count"), len(composers)))
        if len(composers) < 2:
            problems.append("%s: a multi-composed row with %d composer(s)"
                            % (name, len(composers)))
        for site in composers:
            if site.get("role") not in ROLES:
                problems.append("%s: unknown role %r" % (name, site.get("role")))
            if site.get("write_site_count") != len(site.get("writes_this_name_at_lines") or []):
                problems.append("%s: %s write_site_count %r but %d lines"
                                % (name, site.get("source"), site.get("write_site_count"),
                                   len(site.get("writes_this_name_at_lines") or [])))
            want = (D_MUTATES_THEN_RESTORES if (site.get("write_site_count") or 0) >= 2
                    else D_SINGLE_WRITE)
            if site.get("mutation_discipline") != want:
                problems.append("%s: %s discipline %r but %d write sites"
                                % (name, site.get("source"), site.get("mutation_discipline"),
                                   site.get("write_site_count") or 0))
        producers = [c for c in composers if c.get("role") == R_PRODUCER]
        if row.get("has_a_producer_composer") != bool(producers):
            problems.append("%s: has_a_producer_composer disagrees with the composer roles"
                            % name)
        distinct = sorted({c["source"] for c in composers})
        if sorted(row.get("composer_sources") or []) != distinct:
            problems.append("%s: composer_sources %r but the entries name %r"
                            % (name, row.get("composer_sources"), distinct))
        primary = row.get("primary_composer_source")
        if primary not in distinct:
            problems.append("%s: primary source %r is not one of its composers"
                            % (name, primary))
        if producers and primary != sorted({c["source"] for c in producers})[0]:
            problems.append("%s: primary %r is not a producer although producers exist"
                            % (name, primary))
        want_extras = [s for s in distinct if s != primary]
        if sorted(e["source"] for e in (row.get("extras") or [])) != want_extras:
            problems.append("%s: extras %r do not re-derive as %r"
                            % (name, [e.get("source") for e in row.get("extras") or []],
                               want_extras))
        if row.get("extra_composer_count") != len(want_extras):
            problems.append("%s: extra_composer_count %r but %d extras"
                            % (name, row.get("extra_composer_count"), len(want_extras)))
        for extra in row.get("extras") or []:
            if extra.get("role") != role_of(extra.get("source") or ""):
                problems.append("%s: extra role %r does not match its source name"
                                % (name, extra.get("role")))
            want = (D_MUTATES_THEN_RESTORES if (extra.get("write_site_count") or 0) >= 2
                    else D_SINGLE_WRITE)
            if extra.get("mutation_discipline") != want:
                problems.append("%s: extra %s discipline %r but %d write sites"
                                % (name, extra.get("source"),
                                   extra.get("mutation_discipline"),
                                   extra.get("write_site_count") or 0))
        want_all = bool(want_extras) and all(role_of(s) == R_HARNESS for s in want_extras)
        if row.get("extras_are_all_harnesses") != want_all:
            problems.append("%s: extras_are_all_harnesses does not re-derive" % name)
        if row.get("exists_on_disk") and row.get("parses_as_json") is None:
            problems.append("%s: exists but was never parsed" % name)
        if row.get("parses_as_json") is not None and not row.get("exists_on_disk"):
            problems.append("%s: publishes a parse verdict without a file" % name)
    want_verdict = _verdict({k: summary.get(k) for k in derived})
    if face.get("verdict") != want_verdict:
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"), want_verdict))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r is outside the frozen vocabulary" % (face.get("verdict"),))
    re_ans = card_answer(face.get("rows") or [], face.get("leftover_mutant_files") or [])
    pub_ans = face.get("card_answer") or {}
    for key, value in re_ans.items():
        if pub_ans.get(key) != value:
            problems.append("card_answer.%s: published %r, re-derives %r"
                            % (key, pub_ans.get(key), value))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e492 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    s = face.get("summary") or {}
    print("multi=%d extras=%d harness_extras=%d all_harness_faces=%d no_producer=%d "
          "unparseable=%d leftovers=%d"
          % (s.get("multi_composed_faces") or 0,
             s.get("extra_composer_sites") or 0,
             (s.get("extra_composer_sites_by_role") or {}).get(R_HARNESS) or 0,
             s.get("faces_whose_extras_are_all_harnesses") or 0,
             s.get("faces_whose_composers_are_all_harnesses") or 0,
             s.get("faces_left_in_a_mutated_state") or 0,
             s.get("leftover_mutant_files") or 0))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build(root, write=False)
    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved %r -> %r"
                        % (published.get("verdict"), fresh.get("verdict")))
    a = {r["latest_basename"]: r for r in published.get("rows") or []}
    b = {r["latest_basename"]: r for r in fresh.get("rows") or []}
    if set(a) != set(b):
        problems.append("population moved: +%d -%d"
                        % (len(set(b) - set(a)), len(set(a) - set(b))))
    for name in sorted(set(a) & set(b)):
        if a[name].get("composer_count") != b[name].get("composer_count"):
            problems.append("%s: composer count moved %r -> %r"
                            % (name, a[name].get("composer_count"),
                               b[name].get("composer_count")))
        if a[name].get("extra_roles") != b[name].get("extra_roles"):
            problems.append("%s: extra roles moved %r -> %r"
                            % (name, a[name].get("extra_roles"),
                               b[name].get("extra_roles")))
    if len(published.get("leftover_mutant_files") or []) != len(
            fresh.get("leftover_mutant_files") or []):
        problems.append("leftover mutant artefact count moved")
    problems.extend(row_problems(fresh))
    print("e492 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "results", "state_tilt"))
    os.makedirs(os.path.join(root, "results", "quarantine"))

    def w(name, body):
        io.open(os.path.join(root, "scripts", name), "w", encoding="utf-8",
                newline="\n").write(body)

    head = ("import json\nimport os\n"
            "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
            "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n"
            "SLATE = os.path.join(ROOT, 'results', 'quarantine')\n")
    # a producer writes the published name once, with no restore
    w("e900_probe.py", head +
      "def write(rows):\n"
      "    path = os.path.join(OUTDIR, 'alpha_latest.json')\n"
      "    with open(path, 'w') as fh:\n"
      "        json.dump({'rows': rows}, fh)\n")
    # a harness writes the same name twice: mutate, run, put the original back
    w("run_e900_smoke_leg.py", head +
      "FACE = os.path.join(OUTDIR, 'alpha_latest.json')\n"
      "BAK = os.path.join(SLATE, 'alpha.bak')\n"
      "orig = open(FACE).read()\n"
      "open(BAK, 'w').write(orig)\n"
      "data = json.loads(orig)\n"
      "data['rows'] = (data.get('rows') or 0) + 1\n"
      "open(FACE, 'w').write(json.dumps(data))\n"
      "open(FACE, 'w').write(orig)\n")
    # a second harness for the same name -- the extras arm
    w("run_e901_smoke_leg.py", head +
      "open(os.path.join(OUTDIR, 'alpha_latest.json'), 'w').write('{}')\n")
    # a name whose ONLY composers are harnesses: the producer is out of static reach
    w("run_e902_smoke_leg.py", head +
      "open(os.path.join(OUTDIR, 'beta_latest.json'), 'w').write('{}')\n"
      "open(os.path.join(OUTDIR, 'beta_latest.json'), 'w').write('{}')\n")
    # a one-off repair writing a third name twice
    w("_r902_repair.py", head +
      "open(os.path.join(OUTDIR, 'gamma_latest.json'), 'w').write('{}')\n"
      "open(os.path.join(OUTDIR, 'gamma_latest.json'), 'w').write('{}')\n")
    w("e903_writer.py", head +
      "open(os.path.join(OUTDIR, 'gamma_latest.json'), 'w').write('{}')\n")
    # on-disk live arm: alpha parses, beta is left mutated (not JSON), gamma parses
    io.open(os.path.join(root, "results", "state_tilt", "alpha_latest.json"), "w",
            encoding="utf-8", newline="\n").write('{"rows": 2}')
    io.open(os.path.join(root, "results", "state_tilt", "beta_latest.json"), "w",
            encoding="utf-8", newline="\n").write("doctored")
    io.open(os.path.join(root, "results", "state_tilt", "gamma_latest.json"), "w",
            encoding="utf-8", newline="\n").write('{"rows": 1}')
    io.open(os.path.join(root, "results", "state_tilt", "delta_mut.json"), "w",
            encoding="utf-8", newline="\n").write("{}")
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e492_")
    root = _fixture(tmp)
    rows, leftovers, meta = population(root)
    by = {r["latest_basename"]: r for r in rows}
    roles = {c["source"]: c["role"] for c in (by.get("alpha_latest.json") or {}).get("composers") or []}

    leg("the three multi-composed fixture names are found", len(rows) == 3)
    leg("a probe is a producer", roles.get("scripts/e900_probe.py") == R_PRODUCER)
    leg("a leg runner is a harness", roles.get("scripts/run_e900_smoke_leg.py") == R_HARNESS)
    leg("a _rNNN script is a one-off repair",
        role_of("scripts/_r902_repair.py") == R_ONEOFF)
    leg("a harness with two write sites mutates then restores",
        next(c for c in by["alpha_latest.json"]["composers"]
             if c["source"] == "scripts/run_e900_smoke_leg.py")["mutation_discipline"]
        == D_MUTATES_THEN_RESTORES)
    leg("a harness with one write site has no restore",
        next(c for c in by["alpha_latest.json"]["composers"]
             if c["source"] == "scripts/run_e901_smoke_leg.py")["mutation_discipline"]
        == D_SINGLE_WRITE)
    leg("the harness that saves the original away is seen",
        next(c for c in by["alpha_latest.json"]["composers"]
             if c["source"] == "scripts/run_e900_smoke_leg.py")["saves_the_original_away_first"])
    leg("a producer that writes once does not save the original",
        next(c for c in by["alpha_latest.json"]["composers"]
             if c["source"] == "scripts/e900_probe.py")["saves_the_original_away_first"] is False)
    leg("the producer is the primary composer, not the first by name",
        by["alpha_latest.json"]["primary_composer_source"] == "scripts/e900_probe.py")
    leg("the extras of alpha are the two harnesses",
        by["alpha_latest.json"]["extra_roles"] == [R_HARNESS]
        and by["alpha_latest.json"]["extra_composer_count"] == 2)
    leg("a name whose composers are all harnesses has no producer",
        by["beta_latest.json"]["has_a_producer_composer"] is False)
    leg("a one-off repair appears as an extra role",
        by["gamma_latest.json"]["extra_roles"] == [R_ONEOFF])
    leg("the left-behind face is caught by the live arm",
        by["beta_latest.json"]["parses_as_json"] is False)
    leg("a face that parses is not called left behind",
        by["alpha_latest.json"]["parses_as_json"] is True)
    leg("leftover mutant artefacts are listed",
        [f["name"] for f in leftovers] == ["delta_mut.json"])
    face = {"rows": rows, "leftover_mutant_files": leftovers,
            "evidence_cutoff": "2026-11-07"}
    summary = _recompute(face)
    face["summary"] = summary
    face["verdict"] = _verdict(summary)
    face["card_answer"] = card_answer(rows, leftovers)
    leg("the tallies re-derive", summary["multi_composed_faces"] == len(rows))
    leg("the extra-composer count excludes the primary",
        summary["extra_composer_sites"] == 3)
    leg("the harness extras are counted by role",
        summary["extra_composer_sites_by_role"][R_HARNESS] == 2)
    leg("a left-behind face outranks every other verdict",
        face["verdict"] == V_LEFTOVER)
    leg("the card answer names the left-behind face",
        face["card_answer"]["faces_whose_published_copy_does_not_parse"]
        == ["beta_latest.json"])
    leg("the card answer names the all-harness face",
        face["card_answer"]["faces_with_no_producer_composer"] == ["beta_latest.json"])
    leg("the fixture has no row problems", row_problems(face) == [])
    healed = json.loads(json.dumps(face))
    healed["rows"] = [r for r in healed["rows"] if r["latest_basename"] != "beta_latest.json"]
    healed["summary"] = _recompute(healed)
    healed["verdict"] = _verdict(healed["summary"])
    healed["card_answer"] = card_answer(healed["rows"], healed["leftover_mutant_files"])
    leg("with the left-behind face removed the verdict falls back to all-harness",
        healed["verdict"] in (V_ALL, V_MIXED))
    broken = json.loads(json.dumps(face))
    broken["summary"]["extra_composer_sites"] += 1
    leg("a tally that does not re-derive is refused", row_problems(broken))
    broken2 = json.loads(json.dumps(face))
    broken2["verdict"] = V_ALL
    leg("a verdict that contradicts the left-behind face is refused", row_problems(broken2))
    broken3 = json.loads(json.dumps(face))
    broken3["rows"][0]["composers"][0]["role"] = "a_decorator"
    leg("an unknown role is refused", row_problems(broken3))
    broken4 = json.loads(json.dumps(face))
    _row4 = next(r for r in broken4["rows"] if r["extras"])
    _extra4 = _row4["extras"][0]
    _extra4["mutation_discipline"] = (D_SINGLE_WRITE
                                     if _extra4["mutation_discipline"]
                                     == D_MUTATES_THEN_RESTORES
                                     else D_MUTATES_THEN_RESTORES)
    leg("a discipline that contradicts its write sites is refused", row_problems(broken4))
    broken5 = json.loads(json.dumps(face))
    broken5["card_answer"]["leaves_a_mutated_face_behind"] = False
    leg("a card answer that denies the left-behind face is refused", row_problems(broken5))
    leg("write leaves both faces on disk",
        all(os.path.exists(p) for p in _write(face, root)))
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def run(root=None):
    root = root or ROOT
    face = build(root, write=True)
    s = face["summary"]
    print("e492 run verdict=%s" % face["verdict"])
    print("multi_composed=%d composers=%d extras=%d harness_extras=%d oneoff_extras=%d"
          % (s["multi_composed_faces"], s["composer_sites"], s["extra_composer_sites"],
             s["extra_composer_sites_by_role"][R_HARNESS],
             s["extra_composer_sites_by_role"][R_ONEOFF]))
    print("faces_whose_extras_are_all_harnesses=%d faces_with_no_producer=%d "
          "single_write_harness_faces=%d unparseable=%d leftovers=%d"
          % (s["faces_whose_extras_are_all_harnesses"],
             s["faces_whose_composers_are_all_harnesses"],
             s["faces_with_a_single_write_harness"],
             s["faces_left_in_a_mutated_state"], s["leftover_mutant_files"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E492 who the extra latest composers are")
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
