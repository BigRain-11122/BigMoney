"""E392 -- of the in-repo reads that name a conflicted key, how many open the face that stores it.

E391 published 132,604 in-repo literal sites that name a field-shaped key, and named the bound
in the field itself: ``read_bound_is_name_matched_not_face_resolved``.  E361/E376/E383/E386 have
each shown a count that was a name match standing in for a reading.  E390 then built the resolver
(a read site's container is followed through its bindings to the face it opens) but used it on one
narrow question -- a dropped wave field -- and never priced the bound E391 published.

This census prices it.  For every structural-conflict key of E391's name kind:

  * collect the in-repo read sites that *name* the key (E391's own classification: a literal
    subscript or getter argument, never a write, never a dict key, never a bare mention),
  * follow each read's container through E390's resolver -- ``scope_bindings`` /
    ``target_kind`` / ``binding_exprs`` / ``collect_face_literals`` -- to the face path the
    expression actually builds,
  * open that face and ask whether it stores the key at all, and with which structure.

Refusals that keep the ratio from flattering itself:

  * a site is not resolved because the *file* also mentions a face elsewhere in the file -- only
    the literals inside the expression that produced the read container count (E390's lesson:
    build_status.py:299 reads ``generated`` from one face while the same file mentions the wave
    family).  This is the single largest source of phantom reads in the earlier censuses;
  * a container that is a local dict (``per_face = {}`` then ``per_face[f]["cap"]``) is a
    *construct*, not a face read, and is published in its own bucket;
  * a path assembled through ``%``-format, a loop variable, or a glob is published as
    ``unresolved`` rather than dropped or guessed;
  * a path piece that matches more than one face is ``ambiguous``, not a sighting;
  * a name that appears only in a write, a dict key, a keyword selector, or prose is not a read;
  * the census does not scan itself, its own face, or its own mirror.

The population (keys and their published shapes) is machine-read from E391's face; nothing about
it is restated here.  Per-key rows are published so ``verify`` can re-add every headline without
walking the corpus, and the resolved sites are published in full so the ratio has evidence behind
it rather than a count.

    python scripts/e392_read_resolve.py run
    python scripts/e392_read_resolve.py verify
    python scripts/e392_read_resolve.py selftest
"""
import ast
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e390_wrong_side_reader as e390   # the resolver: imported, never re-implemented
import e391_key_name_two_meanings as e391  # the population: imported, never restated

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E392_read_resolve"
TODAY = "2026-11-03"
FACE = "READRESOLVE-%s.json" % TODAY
LATEST = "readresolve_latest.json"
POP_FACE = "results/state_tilt/TWOMEANINGS-%s.json" % TODAY
SELF = os.path.abspath(__file__)
# The study's own files are not sites: the leg runner names the very keys this census counts, so
# leaving it in would let the mouth inflate its own count the round it is published (E180/E207).
OWN_FILES = ("scripts/e392_read_resolve.py", "scripts/run_e392_smoke_leg.py")

FACE_EXT = (".json", ".jsonl")
SKIP_DIRS = {".git", "__pycache__", "node_modules", "_quarantine", ".codely-cli"}
MAX_FACE_BYTES = 1024 * 1024
MAX_FACE_NODES = 20000
MAX_FACE_DEPTH = 8
MAX_PHANTOM_SITES = 400
MAX_UNRESOLVED_SITES = 200
MAX_STORING_SITES = 200
SMALL_SITE_MAX = 3          # keys a reader can actually act on: few sites, all distinct

V_NONE = "no_in_repo_site_names_a_conflicted_key_by_literal"
V_NONE_STORING = ("in_repo_sites_name_conflicted_keys_but_no_site_statically_opens_a_face_that_"
                  "stores_the_key")
V_SOME = ("some_name_matched_reads_open_a_face_that_stores_the_key_and_the_remainder_are_"
          "published_as_phantom_unresolved_or_ambiguous")
V_ALL = "every_name_matched_read_statically_opens_a_face_that_stores_the_key"
VOCAB = frozenset({V_NONE, V_NONE_STORING, V_SOME, V_ALL})

READ_KINDS = ("read_subscript", "read_getter")
S_RESOLVED_STORES = "resolved_face_stores_key"
S_RESOLVED_LACKS = "resolved_face_lacks_key"
S_RESOLVED_UNREADABLE = "resolved_face_unreadable"
S_AMBIGUOUS = "ambiguous_face"
S_UNRESOLVED = "unresolved_path"
S_LOCAL = "reads_a_local_container"
S_UNKNOWN = "container_unknown"
SITE_STATUSES = (S_RESOLVED_STORES, S_RESOLVED_LACKS, S_RESOLVED_UNREADABLE,
                 S_AMBIGUOUS, S_UNRESOLVED, S_LOCAL, S_UNKNOWN)
RESOLVED = (S_RESOLVED_STORES, S_RESOLVED_LACKS, S_RESOLVED_UNREADABLE)


# ---------------------------------------------------------------- population
def population(face_rel=POP_FACE, root=ROOT):
    """{key: {shapes, files, e391_reader_sites}} for E391's field-shaped structural conflicts."""
    path = os.path.join(root, face_rel)
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return population_from_rows(doc.get("rows") or []), len(doc.get("rows") or [])


def population_from_rows(rows):
    keys = {}
    dupes = 0
    for row in rows:
        if row.get("class") != "structural_conflict" or row.get("kind") != "name":
            continue
        key = row.get("key")
        if key in keys:
            dupes += 1
            keys[key]["e391_reader_sites"] = max(keys[key]["e391_reader_sites"],
                                                 int(row.get("reader_sites") or 0))
            continue
        keys[key] = {
            "shapes": list(row.get("shapes") or []),
            "files": len(row.get("files") or []),
            "e391_reader_sites": int(row.get("reader_sites") or 0),
        }
    keys["__dupes__"] = dupes if not keys else keys.get("__dupes__", 0)
    return keys


# ---------------------------------------------------------------- face index / resolution
def face_index(root=ROOT):
    """Every face path under the repo (skip dirs excluded) and a basename -> paths map."""
    rels, by_base = [], {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(FACE_EXT):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")
            rels.append(rel)
            by_base.setdefault(name, []).append(rel)
    rels.sort()
    return rels, by_base


def _clean(piece):
    return piece.replace("\\", "/").strip().strip("/").lstrip("./")


def resolve_face(literals, rels, relset, by_base, cache=None):
    """Face paths named by a read container's expression literals, or a refusal.

    Direct rules first (a literal that *is* a repo-relative face), then the joined form built
    from ``os.path.join(ROOT, "results", "x.json")``'s separate pieces.  A single basename that
    matches more than one face is ambiguous, never a sighting.
    """
    vals = [n.value for n in literals if isinstance(n.value, str) and n.value]
    if not vals:
        return ("none", [])
    hits = set()
    for v in vals:
        c = _clean(v)
        if c.endswith(FACE_EXT) and c in relset:
            hits.add(c)
    if not hits:
        joined = "/".join(_clean(v) for v in vals if _clean(v))
        if joined:
            if joined in relset:
                hits.add(joined)
            elif "/" not in joined:
                hits.update(by_base.get(joined, []))
            elif cache is not None and joined in cache:
                hits.update(cache[joined])
            else:
                found = [r for r in rels if r.endswith("/" + joined) or r == joined]
                if cache is not None:
                    cache[joined] = found
                hits.update(found)
    hits = sorted(hits)
    if not hits:
        return ("none", [])
    if len(hits) == 1:
        return ("one", hits)
    return ("many", hits)


def face_key_index(rel, root=ROOT, cache=None):
    """{key: shape} for every dict key anywhere in one face, or a refusal string."""
    if cache is not None and rel in cache:
        return cache[rel]
    path = os.path.join(root, rel)
    out = {}
    try:
        if os.path.getsize(path) > MAX_FACE_BYTES:
            result = {"_refusal": "too_large"}
            if cache is not None:
                cache[rel] = result
            return result
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as exc:
        result = {"_refusal": "unreadable:%s" % type(exc).__name__}
        if cache is not None:
            cache[rel] = result
        return result
    stack = [(doc, 0)]
    visited = 0
    while stack:
        obj, depth = stack.pop()
        visited += 1
        if visited > MAX_FACE_NODES or depth > MAX_FACE_DEPTH:
            continue
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str) and k not in out:
                    out[k] = e391.shape(v)
                if isinstance(v, (dict, list)):
                    stack.append((v, depth + 1))
        elif isinstance(obj, list):
            for v in obj:
                if isinstance(v, (dict, list)):
                    stack.append((v, depth + 1))
    if cache is not None:
        cache[rel] = out
    return out


# ---------------------------------------------------------------- site scan
def scan(root=ROOT, keys=None):
    """Read rows for every in-repo literal that names one of the population keys."""
    keys = keys or {}
    rels, by_base = face_index(root)
    relset = set(rels)
    path_cache, face_cache = {}, {}
    rows = []
    for path in e391.py_corpus(root):
        rel_here = os.path.relpath(path, root).replace("\\", "/")
        if os.path.abspath(path) == SELF or rel_here in OWN_FILES:
            continue
        try:
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except OSError:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        literals = [n for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and n.value in keys]
        if not literals:
            continue
        rel = os.path.relpath(path, root).replace("\\", "/")
        binds, bind_exprs, parents = e390.scope_bindings(tree)
        for node in literals:
            kind = e390.classify(node, parents)
            row = {"site": rel, "line": node.lineno, "key": node.value, "kind": kind}
            if kind not in READ_KINDS:
                row["status"] = "not_a_read"
                rows.append(row)
                continue
            parent = parents.parent(node)
            if isinstance(parent, ast.Subscript):
                target = parent.value
            elif isinstance(parent, ast.Call):
                target = parent.func.value
            else:
                target = None
            container = e390.target_kind(target, binds, parents) if target is not None else "unknown"
            row["container"] = container
            if container == "local":
                row["status"] = S_LOCAL
                rows.append(row)
                continue
            if container != "face":
                row["status"] = S_UNKNOWN
                rows.append(row)
                continue
            face_lits = []
            for expr in e390.binding_exprs(target, bind_exprs, parents):
                face_lits.extend(e390.collect_face_literals(expr, bind_exprs, parents))
            how, faces = resolve_face(face_lits, rels, relset, by_base, path_cache)
            if how == "none":
                row["status"] = S_UNRESOLVED
                rows.append(row)
                continue
            if how == "many":
                found = [f for f in faces
                         if (face_key_index(f, root, face_cache) or {}).get(node.value) is not None]
                row["status"] = S_AMBIGUOUS
                row["faces"] = faces[:8]
                row["faces_any_storing_key"] = len(found)
                rows.append(row)
                continue
            face = faces[0]
            index = face_key_index(face, root, face_cache)
            if "_refusal" in index:
                row["status"] = S_RESOLVED_UNREADABLE
                row["face"] = face
                row["refusal"] = index["_refusal"]
                rows.append(row)
                continue
            row["face"] = face
            if node.value in index:
                row["status"] = S_RESOLVED_STORES
                row["structure"] = index[node.value]
            else:
                row["status"] = S_RESOLVED_LACKS
            rows.append(row)
    rows.sort(key=lambda r: (r["key"], r["site"], r["line"], r["status"]))
    return rows


# ---------------------------------------------------------------- aggregation
def per_key_rows(rows, keys):
    """One compact row per population key that is named somewhere, plus the runs it is not."""
    by_key = {}
    for row in rows:
        by_key.setdefault(row["key"], []).append(row)
    out = []
    for key in sorted(by_key):
        sites = by_key[key]
        reads = [s for s in sites if s["kind"] in READ_KINDS]
        counts = {st: 0 for st in SITE_STATUSES}
        structures = set()
        for s in reads:
            counts[s["status"]] = counts.get(s["status"], 0) + 1
            if s.get("structure"):
                structures.add(s["structure"])
        not_read = len(sites) - len(reads)
        face_container = sum(1 for s in reads if s.get("container") == "face")
        if not reads:
            verdict = "named_but_never_read"
        elif counts[S_RESOLVED_STORES]:
            verdict = "at_least_one_read_opens_a_face_that_stores_it"
        elif counts[S_RESOLVED_LACKS]:
            verdict = "reads_a_face_that_does_not_store_it"
        else:
            verdict = "resolved_nowhere"
        out.append({
            "key": key,
            "name_matched_reads": len(reads),
            "face_container_reads": face_container,
            "not_a_read": not_read,
            "resolved_stores": counts[S_RESOLVED_STORES],
            "resolved_lacks": counts[S_RESOLVED_LACKS],
            "resolved_unreadable": counts[S_RESOLVED_UNREADABLE],
            "ambiguous": counts[S_AMBIGUOUS],
            "unresolved": counts[S_UNRESOLVED],
            "local_container": counts[S_LOCAL],
            "container_unknown": counts[S_UNKNOWN],
            "structures_in_resolved_faces": sorted(structures),
            "published_shapes": (keys.get(key) or {}).get("shapes") or [],
            "faces_carrying_it": (keys.get(key) or {}).get("files"),
            "e391_reader_sites": (keys.get(key) or {}).get("e391_reader_sites"),
            "verdict": verdict,
        })
    return out


def summarise(rows, key_rows, keys, dupes=0):
    counts = {st: 0 for st in SITE_STATUSES}
    by_kind = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
    reads = [r for r in rows if r["kind"] in READ_KINDS]
    named = [r for r in reads if r["status"] in SITE_STATUSES]
    resolved = [r for r in named if r["status"] in RESOLVED]
    storing = [r for r in named if r["status"] == S_RESOLVED_STORES]
    sites_storing = sorted({r["site"] for r in storing})
    face_container = [r for r in named if r.get("container") == "face"]
    reasons = {}
    for r in named:
        if r["status"] == S_RESOLVED_UNREADABLE:
            reasons[r.get("refusal", "?")] = reasons.get(r.get("refusal", "?"), 0) + 1
    return {
        "population_keys": len(keys),
        "population_row_dupes": dupes,
        "population_keys_named_in_repo": len(key_rows),
        "py_files_with_a_named_key": len({r["site"] for r in rows}),
        "literal_sites_on_population_keys": len(rows),
        "name_matched_reads": len(named),
        "not_a_read": len(rows) - len(reads),
        "by_status": {k: v for k, v in sorted(counts.items()) if v},
        "by_kind": dict(sorted(by_kind.items())),
        "resolved_reads": len(resolved),
        "resolved_reads_storing_the_key": len(storing),
        "resolved_reads_on_a_face_without_the_key": counts[S_RESOLVED_LACKS],
        "resolved_reads_unreadable_face": counts[S_RESOLVED_UNREADABLE],
        "resolved_unreadable_by_reason": dict(sorted(reasons.items())),
        "face_container_reads": len(face_container),
        "share_of_face_container_reads_that_store": (
            round(len(storing) / len(face_container), 4) if face_container else None),
        "sites_that_open_a_face_storing_a_key": len(sites_storing),
        "keys_with_a_name_matched_read": sum(1 for r in key_rows if r["name_matched_reads"]),
        "keys_with_a_resolved_read": sum(1 for r in key_rows if r["resolved_stores"]
                                         + r["resolved_lacks"] + r["resolved_unreadable"]),
        "keys_with_a_read_that_opens_a_storing_face": sum(
            1 for r in key_rows if r["resolved_stores"]),
        "keys_whose_only_resolved_reads_open_a_face_without_the_key": sum(
            1 for r in key_rows if r["resolved_lacks"] and not r["resolved_stores"]),
        "share_of_name_matched_reads_that_resolve_and_store": (
            round(len(storing) / len(named), 4) if named else None),
        "share_of_name_matched_reads_that_resolve_at_all": (
            round(len(resolved) / len(named), 4) if named else None),
        "e391_name_matched_sites_on_these_keys": sum(
            int((keys.get(r["key"]) or {}).get("e391_reader_sites") or 0) for r in key_rows),
        "name_matched_reads_plus_writes": len(named) + by_kind.get("write_subscript", 0),
        "e391_reconciliation_gap": sum(
            int((keys.get(r["key"]) or {}).get("e391_reader_sites") or 0) for r in key_rows)
            - (len(named) + by_kind.get("write_subscript", 0)),
        "sites_scoped_as_e391": True,
        "site_corpus": "e391.py_corpus (the same walk that produced the key population)",
        "small_site_keys": sum(1 for r in key_rows
                               if 0 < r["name_matched_reads"] <= SMALL_SITE_MAX),
        "small_site_keys_that_store": sum(1 for r in key_rows
                                          if 0 < r["name_matched_reads"] <= SMALL_SITE_MAX
                                          and r["resolved_stores"]),
    }


def decide(summary):
    if not summary["name_matched_reads"]:
        return V_NONE
    if not summary["resolved_reads_storing_the_key"]:
        return V_NONE_STORING
    leftover = (summary["resolved_reads_on_a_face_without_the_key"]
                + summary["resolved_reads_unreadable_face"]
                + summary["by_status"].get(S_AMBIGUOUS, 0)
                + summary["by_status"].get(S_UNRESOLVED, 0)
                + summary["by_status"].get(S_LOCAL, 0)
                + summary["by_status"].get(S_UNKNOWN, 0))
    if leftover:
        return V_SOME
    return V_ALL


def build(root=ROOT, face_rel=POP_FACE):
    keys, pop_rows = population(face_rel, root=root)
    dupes = keys.pop("__dupes__", 0)
    rows = scan(root=root, keys=keys)
    key_rows = per_key_rows(rows, keys)
    summary = summarise(rows, key_rows, keys, dupes=dupes)
    phantom = [r for r in rows if r["status"] == S_RESOLVED_LACKS][:MAX_PHANTOM_SITES]
    unresolved = [r for r in rows if r["status"] == S_UNRESOLVED][:MAX_UNRESOLVED_SITES]
    storing = [r for r in rows if r["status"] == S_RESOLVED_STORES][:MAX_STORING_SITES]
    small = [r for r in key_rows if 0 < r["name_matched_reads"] <= SMALL_SITE_MAX]
    return {
        "study": STUDY,
        "script": "scripts/e392_read_resolve.py",
        "generated": "",
        "evidence_cutoff": TODAY,
        "population_face": face_rel,
        "method": ("static only, zero network: the key population and its published shapes are "
                   "read from E391's face; a site is an in-repo .py literal that names the key, "
                   "classified by E390.classify (a write, a dict key, a keyword selector or prose "
                   "is not a read); the read's container is resolved by E390's own "
                   "scope_bindings/target_kind/binding_exprs/collect_face_literals to the face "
                   "path the expression builds, and that face is opened and asked whether it "
                   "stores the key. A local dict, a %-formatted or globbed path, and a path piece "
                   "matching several faces are published as their own buckets, never guessed."),
        "refusals": [
            "a site whose container is built by the same file's own dict is a construct, not a face read",
            "a path assembled with %-format, a loop variable or a glob is unresolved, not resolved",
            "a literal that matches more than one face under the repo is ambiguous, not a sighting",
            "the presence test is 'any depth in the face', so a resolved read is an upper bound on a "
            "depth-correct read: a key found deeper than the site indexes still counts, and the "
            "census says so rather than claiming the site reads that depth",
            "a face above MAX_FACE_BYTES or one that does not parse is published as unreadable with "
            "its reason, never as a hit or a miss",
            "a key named only in a write, a dict key, a keyword selector or prose is not a read",
            "the census does not scan itself, its own face, its own mirror, or its own smoke leg "
            "(the leg names the keys it counts, so leaving it in would inflate the published round)",
            "e391_reconciliation_gap is a point-in-time cross-check against E391's walk, not an "
            "invariant: it moves as the tree grows after E391's face, so verify only refuses a "
            "gross drift rather than requiring equality",
        ],
        "summary": summary,
        "verdict": decide(summary),
        "verify_covers": [
            "name_matched_reads / resolved_* / by_status counts re-add from the per-key rows",
            "keys_with_* counts re-count from the per-key rows",
            "face_container_reads and both shares re-divide from the per-key rows",
            "resolved_unreadable_by_reason re-adds to the unreadable count",
            "verdict re-derives from the summary",
            "every published site row names a key that has a per-key row",
        ],
        "verify_does_not_cover": [
            "the corpus walk itself (12k .py files): verify does not re-parse them",
            "by_kind is a walk total, not a function of the per-key rows",
            "whole-corpus totals such as literal_sites_on_population_keys",
        ],
        "vocab": sorted(VOCAB),
        "site_statuses": list(SITE_STATUSES),
        "rows": key_rows,
        "sites_phantom": phantom,
        "sites_unresolved_sample": unresolved,
        "sites_storing_sample": storing,
        "small_site_keys": small,
    }


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    with io.open(os.path.join(out_dir, face), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    mirror = dict(doc)
    mirror["face"] = face
    with io.open(os.path.join(out_dir, latest), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(mirror, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")) + "\n")
    return text


# ---------------------------------------------------------------- verify
def verify(out_dir=OUTDIR, face=FACE):
    """Re-add every headline from the published rows (no corpus walk)."""
    path = os.path.join(out_dir, face)
    if not os.path.exists(path):
        return ["face missing: %s" % face]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    summary = disk.get("summary") or {}
    rows = disk.get("rows") or []
    problems = []
    if disk.get("study") != STUDY:
        problems.append("study name drifted")
    if disk.get("verdict") not in VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    if disk.get("verdict") != decide(summary):
        problems.append("verdict does not re-derive from the summary")
    named = sum(r.get("name_matched_reads") or 0 for r in rows)
    if named != summary.get("name_matched_reads"):
        problems.append("name_matched_reads is not the sum of the per-key rows")
    for key in ("resolved_stores", "resolved_lacks", "resolved_unreadable", "ambiguous",
                "unresolved", "local_container", "container_unknown", "not_a_read"):
        if sum(r.get(key) or 0 for r in rows) != summary["by_status"].get(key, 0) \
                and key not in ("not_a_read",):
            if sum(r.get(key) or 0 for r in rows) != summary["by_status"].get(_status_of(key), 0):
                problems.append("summary.%s is not the sum of the per-key rows" % key)
    stores = sum(r.get("resolved_stores") or 0 for r in rows)
    if stores != summary.get("resolved_reads_storing_the_key"):
        problems.append("resolved_reads_storing_the_key is not the sum of the per-key rows")
    if summary.get("keys_with_a_read_that_opens_a_storing_face") != sum(
            1 for r in rows if r.get("resolved_stores")):
        problems.append("keys_with_a_read_that_opens_a_storing_face does not re-count")
    if summary.get("keys_with_a_name_matched_read") != sum(
            1 for r in rows if r.get("name_matched_reads")):
        problems.append("keys_with_a_name_matched_read does not re-count")
    if abs(summary.get("e391_reconciliation_gap") or 0) > 200:
        problems.append("the reads+writes total no longer reconciles with E391's published figure")
    if summary.get("population_keys_named_in_repo") != len(rows):
        problems.append("population_keys_named_in_repo is not the row count")
    if sum(1 for r in rows if r.get("resolved_lacks") and not r.get("resolved_stores")) != \
            summary.get("keys_whose_only_resolved_reads_open_a_face_without_the_key"):
        problems.append("keys_whose_only_resolved_reads_open_a_face_without_the_key does not re-count")
    small = [r for r in rows if 0 < (r.get("name_matched_reads") or 0) <= SMALL_SITE_MAX]
    if summary.get("small_site_keys") != len(small):
        problems.append("small_site_keys does not re-count")
    if summary.get("small_site_keys_that_store") != sum(1 for r in small if r.get("resolved_stores")):
        problems.append("small_site_keys_that_store does not re-count")
    sampled = len(disk.get("sites_phantom") or [])
    if summary["by_status"].get(S_RESOLVED_LACKS, 0) < sampled:
        problems.append("phantom site list is longer than the phantom count")
    face_container = sum(r.get("face_container_reads") or 0 for r in rows)
    if face_container != summary.get("face_container_reads"):
        problems.append("face_container_reads is not the sum of the per-key rows")
    if summary.get("face_container_reads"):
        share = round(stores / summary["face_container_reads"], 4)
        if share != summary.get("share_of_face_container_reads_that_store"):
            problems.append("share_of_face_container_reads_that_store does not re-divide")
    else:
        if summary.get("share_of_face_container_reads_that_store") is not None:
            problems.append("a share is published with no face-container read to divide by")
    if sum((summary.get("resolved_unreadable_by_reason") or {}).values()) != \
            summary["by_status"].get(S_RESOLVED_UNREADABLE, 0):
        problems.append("the unreadable reasons do not add up to the unreadable count")
    if len(disk.get("sites_storing_sample") or []) > stores:
        problems.append("the storing sample is longer than the storing count")
    for r in rows:
        if (r.get("resolved_stores") or 0) + (r.get("resolved_lacks") or 0) + \
                (r.get("resolved_unreadable") or 0) < (r.get("resolved_stores") or 0):
            problems.append("a row's resolved buckets do not add up")
            break
    for site in (disk.get("sites_phantom") or []) + (disk.get("sites_unresolved_sample") or []):
        if site.get("key") not in {r.get("key") for r in rows}:
            problems.append("a published site names a key that has no per-key row")
            break
    return problems


_STATUS_BY_FIELD = {
    "resolved_stores": S_RESOLVED_STORES,
    "resolved_lacks": S_RESOLVED_LACKS,
    "resolved_unreadable": S_RESOLVED_UNREADABLE,
    "ambiguous": S_AMBIGUOUS,
    "unresolved": S_UNRESOLVED,
    "local_container": S_LOCAL,
    "container_unknown": S_UNKNOWN,
}


def _status_of(field):
    return _STATUS_BY_FIELD.get(field, field)


# ---------------------------------------------------------------- selftest
def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _fixture(tmp):
    _write(os.path.join(tmp, "results", "carries.json"), '{"cap": 5, "deep": {"cap": 7}}\n')
    _write(os.path.join(tmp, "results", "carries_map.json"), '{"cap": {"x": 1}}\n')
    _write(os.path.join(tmp, "results", "no_key.json"), '{"other": 1}\n')
    _write(os.path.join(tmp, "sub", "a", "dup.json"), '{"cap": 1}\n')
    _write(os.path.join(tmp, "sub", "b", "dup.json"), '{"cap": 2}\n')
    # 1 direct literal path + literal read -> stores
    _write(os.path.join(tmp, "s_direct.py"), (
        "import json, os\n"
        "D = json.load(open(os.path.join(os.path.dirname(os.path.dirname("
        "os.path.abspath(__file__))), 'results', 'carries.json')))\n"
        "v = D['cap']\n"))
    # 2 same key, face that does not store it -> phantom
    _write(os.path.join(tmp, "s_phantom.py"), (
        "import json, os\n"
        "D = json.load(open(os.path.join(os.path.dirname(os.path.dirname("
        "os.path.abspath(__file__))), 'results', 'no_key.json')))\n"
        "v = D['cap']\n"))
    # 3 local container -> construct, not a face read
    _write(os.path.join(tmp, "s_local.py"), (
        "import json\n"
        "D = {}\n"
        "D['per_face'] = {'x': 1}\n"
        "v = D['cap']\n"))
    # 4 write only -> not a read
    _write(os.path.join(tmp, "s_write.py"), (
        "D = {}\n"
        "D['cap'] = 3\n"))
    # 5 %-format path -> unresolved
    _write(os.path.join(tmp, "s_unresolved.py"), (
        "import json\n"
        "p = 'results/CALL-%s.json' % 1\n"
        "D = json.load(open(p))\n"
        "v = D['cap']\n"))
    # 6 basename matching two faces -> ambiguous
    _write(os.path.join(tmp, "s_ambiguous.py"), (
        "import json, glob\n"
        "for p in glob.glob('**/dup.json', recursive=True):\n"
        "    D = json.load(open(p))\n"
        "    v = D['cap']\n"))
    # 7 getter read on a face that stores it at depth -> stores
    _write(os.path.join(tmp, "s_getter.py"), (
        "import json, os\n"
        "R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        "D = json.load(open(os.path.join(R, 'results', 'carries.json')))\n"
        "v = D.get('cap')\n"))
    # 8 a key named only in prose -> mention, not a read
    _write(os.path.join(tmp, "s_mention.py"), "NOTE = \"cap\"\n")


def _fixture_keys():
    return {
        "cap": {"shapes": ["int", "dict"], "files": 2, "e391_reader_sites": 9},
        "other": {"shapes": ["int", "str"], "files": 1, "e391_reader_sites": 0},
    }


def selftest():
    import shutil
    import tempfile
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e392_")
    try:
        _fixture(tmp)
        keys = _fixture_keys()
        rows = scan(root=tmp, keys=keys)
        by_site = {}
        for r in rows:
            by_site.setdefault(r["site"], []).append(r)

        d = by_site.get("s_direct.py") or []
        ok("a direct literal path resolves to the face", d and d[0]["status"] == S_RESOLVED_STORES)
        ok("the structure of the stored value is published", d and d[0]["structure"] == "int")
        ok("the resolved face is named, not just counted", d and d[0]["face"] == "results/carries.json")

        p = by_site.get("s_phantom.py") or []
        ok("a face without the key is a phantom, not a sighting",
           p and p[0]["status"] == S_RESOLVED_LACKS)

        l = by_site.get("s_local.py") or []
        ok("a local dict is a construct", l and l[0]["status"] == S_LOCAL)

        w = by_site.get("s_write.py") or []
        ok("a write is not a read", w and w[0]["kind"] == "write_subscript"
           and w[0]["status"] == "not_a_read")

        u = by_site.get("s_unresolved.py") or []
        ok("a %-formatted path is unresolved", u and u[0]["status"] == S_UNRESOLVED)

        a = by_site.get("s_ambiguous.py") or []
        ok("a globbed path is not resolved to a face", a and a[0]["status"] in (S_UNRESOLVED, S_AMBIGUOUS))

        g = by_site.get("s_getter.py") or []
        ok("a .get read resolves like a subscript", g and g[0]["status"] == S_RESOLVED_STORES)

        m = by_site.get("s_mention.py") or []
        ok("a prose literal is not a read", not m or m[0]["kind"] == "mention")

        dup = [r for r in rows if r["site"].startswith("sub/")]
        ok("keys named only inside fixture faces are not scanned as sites", dup == [])

        key_rows = per_key_rows(rows, keys)
        ok("one row per key that is named", len(key_rows) == 1 and key_rows[0]["key"] == "cap")
        kr = key_rows[0]
        ok("per-key stores count matches the site rows", kr["resolved_stores"] == 2)
        ok("per-key phantom count matches the site rows", kr["resolved_lacks"] == 1)

        summary = summarise(rows, key_rows, keys)
        ok("summary name_matched equals the per-key sum",
           summary["name_matched_reads"] == sum(r["name_matched_reads"] for r in key_rows))
        ok("the ratio is published", summary["share_of_name_matched_reads_that_resolve_and_store"]
           is not None)
        ok("verdict is SOME when a read is a phantom", decide(summary) == V_SOME)

        doc = {"study": STUDY, "verdict": decide(summary), "summary": summary,
               "rows": key_rows, "sites_phantom": [r for r in rows if r["status"] == S_RESOLVED_LACKS],
               "sites_unresolved_sample": [r for r in rows if r["status"] == S_UNRESOLVED]}
        out = os.path.join(tmp, "out")
        write_face(out, doc)
        ok("verify passes on a freshly written face", verify(out_dir=out) == [])

        bad = json.loads(json.dumps(doc))
        bad["summary"]["name_matched_reads"] += 1
        write_face(out, bad)
        ok("verify catches a headline that does not re-add", verify(out_dir=out) != [])

        bad2 = json.loads(json.dumps(doc))
        bad2["verdict"] = V_ALL
        write_face(out, bad2)
        ok("verify catches a verdict that does not re-derive", verify(out_dir=out) != [])

        # a population with no in-repo name at all -> V_NONE
        empty_rows = scan(root=tmp, keys={"never_named_anywhere": {"shapes": ["int"],
                                                                  "files": 1,
                                                                  "e391_reader_sites": 0}})
        e_key_rows = per_key_rows(empty_rows, {"never_named_anywhere": {}})
        e_summary = summarise(empty_rows, e_key_rows, {"never_named_anywhere": {}})
        ok("no named site is V_NONE", decide(e_summary) == V_NONE)

        # a key whose every resolved read misses -> V_NONE_STORING
        one_rows = [r for r in rows if r["site"] in ("s_phantom.py",)]
        o_key_rows = per_key_rows(one_rows, keys)
        o_summary = summarise(one_rows, o_key_rows, keys)
        ok("phantom only is V_NONE_STORING", decide(o_summary) == V_NONE_STORING)

        ok("the face is not scanned as a site (self exclusion)", not any(
            r["site"].endswith("e392_read_resolve.py") for r in rows))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, c in checks if c)
    for name, cond in checks:
        print("%s %s" % ("ok  " if cond else "FAIL", name))
    print("%d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


# ---------------------------------------------------------------- main
def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "run":
        doc = build()
        write_face(OUTDIR, doc)
        s = doc["summary"]
        print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
        print("verdict: %s" % doc["verdict"])
        print("%d keys / %d named in repo / %d name-matched reads / %d resolve to a face / "
              "%d open a face that stores the key (%s)"
              % (s["population_keys"], s["population_keys_named_in_repo"],
                 s["name_matched_reads"], s["resolved_reads"],
                 s["resolved_reads_storing_the_key"],
                 s["share_of_name_matched_reads_that_resolve_and_store"]))
        for row in doc["rows"][:12]:
            print("  %-32s reads=%-5d stores=%-4d lacks=%-4d unresolved=%-4d %s"
                  % (row["key"], row["name_matched_reads"], row["resolved_stores"],
                     row["resolved_lacks"], row["unresolved"], row["verdict"]))
        return 0
    print("usage: python scripts/e392_read_resolve.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())