"""E494 -- do the other 49 multi-composed latest faces carry a composer that authors a
payload of its own, and how many of those writes have no restore in the same source?

E493 (r1519) ran the payload-authorship arm on the two faces E492 flagged as
single-write-with-no-restore and found that neither harness authors a payload: both disk
copies are their producers'.  That arm covered 2 of E492's 51 multi-composed names.  The
other 49 were never asked, and the question matters because a harness that writes a
document it built itself into the published path, and never puts the original back, can
leave a mutant on disk that every downstream reader will believe.

This study reads E492's population (never restates it) and, for every composer E492
labelled a doctor harness or a one-off repair, answers three things from that composer's
own source:

  a. which of its write sites really put bytes on the published basename (folded
     independently of E492's line list, so a site E492 missed is published as missed and
     a line E492 credited that writes something else is published as not this face);
  b. what each of those writes puts there -- a saved backup of the same face, a payload
     the source constructs (dumps / a dict literal / a name bound to either), or a file
     copied from somewhere else;
  c. whether the same source ever writes a saved backup back to that basename, and
     whether that restore sits in a ``finally``.

Where a composer authors a payload and never restores it, the disk copy is re-derived
from the face's producer (E493's producer arm, reused) so the answer is not just "this
source could have", but "and here is whether the copy on disk is the producer's".

Writes results/state_tilt/LATESTAUTHOR-<cutoff>.json plus latestauthors_latest.json.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "latestauthors_latest.json"
DATED_PREFIX = "LATESTAUTHOR"
EVIDENCE_CUTOFF = "2026-11-07"
CARD = ("E494-DO-THE-OTHER-49-MULTI-COMPOSED-FACES-CARRY-A-COMPOSER-THAT-AUTHORS-A-"
        "PAYLOAD-OF-ITS-OWN")
SELF_EXCLUDED = ("e494_", "run_e494")

SOURCE_FACE_GLOB = "LATESTDOCTOR-"
PRIOR_FACE_GLOB = "LATESTCOPYOWNER-"

R_HARNESS = "a_doctor_harness"
R_ONEOFF = "a_one_off_repair"
R_PRODUCER = "a_producer"
EXTRA_ROLES = (R_HARNESS, R_ONEOFF)

# What a write puts on the published basename.
P_BACKUP = "a_saved_backup_of_the_same_face"
P_CONSTRUCTED = "a_payload_the_source_constructs"
P_COPIED = "bytes_copied_from_another_path"
P_EMPTY = "an_empty_or_truncated_write"
P_UNKNOWN = "a_payload_this_build_cannot_classify"
PAYLOAD_VOCAB = (P_BACKUP, P_CONSTRUCTED, P_COPIED, P_EMPTY, P_UNKNOWN)

# Per (face, composer) answer.
C_AUTHORS_AND_RESTORES = "authors_a_payload_and_puts_the_original_back"
C_AUTHORS_NO_RESTORE = "authors_a_payload_and_has_no_restore_in_its_source"
C_BACKUP_ONLY = "writes_only_a_saved_backup_of_the_face"
C_NEVER_WRITES = "never_writes_the_published_basename"
CLASS_VOCAB = (C_AUTHORS_AND_RESTORES, C_AUTHORS_NO_RESTORE, C_BACKUP_ONLY, C_NEVER_WRITES)

V_ALL_RESTORE = ("every_extra_composer_that_authors_a_payload_puts_the_original_back_in_its_"
                 "own_source")
V_SOME_NO_RESTORE = ("some_extra_composer_authors_a_payload_with_no_restore_in_its_own_source")
V_NONE_AUTHOR = "no_extra_composer_authors_a_payload_of_its_own"
V_EMPTY = "no_face_carries_an_extra_harness_or_repair_composer"
V_ERROR = "a_face_could_not_be_measured_in_this_environment"
VERDICT_VOCAB = (V_ALL_RESTORE, V_SOME_NO_RESTORE, V_NONE_AUTHOR, V_EMPTY, V_ERROR)

WRITE_HANDLE_CALLS = ("open", "io.open")
PAYLOAD_CALLS = ("dumps", "dump", "encode", "format", "dumps_indent")
COPY_CALLS = ("copyfile", "copy", "copy2", "move")
MOVE_CALLS = ("replace", "rename")
WRITE_METHODS = ("write", "write_text", "write_bytes")
MAX_NAME_HOPS = 2

# The parent face's own words.  Kept as literals so a change on either side shows up as a
# disagreement rather than passing silently: E492 decided "mutates then restores" from a
# write-site COUNT, not from a restore it had found.
D_PARENT_RESTORES = "writes_the_name_twice_so_it_can_put_the_original_back"
D_PARENT_SINGLE = "writes_the_name_once_with_no_restore_in_the_same_source"


def _rel(path):
    path = os.path.abspath(path)
    if path.startswith(ROOT + os.sep):
        return path[len(ROOT) + 1:].replace(os.sep, "/")
    return path


def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _call_name(node):
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _func_tail(node):
    """Last attribute of a call target: ``json.dumps`` -> ``dumps``, ``io.open`` -> ``open``."""
    return _call_name(node) if isinstance(node, (ast.Name, ast.Attribute)) else ""


# ---------------------------------------------------------------------------------------------
# basename folding -- what a path expression on this tree could name
# ---------------------------------------------------------------------------------------------
def _literal_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _collect_consts(tree):
    """Module-level and function-level ``NAME = <str or join(...)>`` bindings, ordered."""
    consts = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name):
                vals = _fold_string(node.value, consts, hops=MAX_NAME_HOPS)
                if vals:
                    consts[tgt.id] = vals
    return consts


def _fold_string(node, consts, hops=MAX_NAME_HOPS):
    """Fold an expression to a set of candidate path strings (best effort, no guessing)."""
    lit = _literal_str(node)
    if lit is not None:
        return {lit}
    if isinstance(node, ast.Name):
        if hops <= 0:
            return set()
        return set(consts.get(node.id) or set())
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append([v.value])
            elif isinstance(v, ast.FormattedValue):
                inner = _fold_string(v.value, consts, hops - 1)
                if not inner:
                    return set()
                parts.append(sorted(inner))
            else:
                return set()
        out = [""]
        for chunk in parts:
            out = [a + b for a in out for b in chunk]
        return set(out)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _fold_string(node.left, consts, hops)
        right = _fold_string(node.right, consts, hops)
        if not left or not right:
            return set()
        return {a + b for a in left for b in right}
    if isinstance(node, ast.Call):
        tail = _func_tail(node.func)
        if tail == "join" and node.args:
            # The file name is the last component; unknown directories must not sink it.
            leaf = _fold_string(node.args[-1], consts, hops)
            if not leaf:
                return set()
            dirs = [""]
            if len(node.args) > 1:
                head = _fold_string(
                    ast.Call(func=node.func, args=node.args[:-1], keywords=[]),
                    consts, hops)
                if head:
                    dirs = sorted(head)
                else:
                    # the directory part is unknown (ROOT, __file__ chains): keep the leaf
                    return {os.path.join("?", s) for s in leaf}
            return {os.path.join(d, s) for d in dirs for s in leaf}
        if tail in ("str", "Path", "fspath") and node.args:
            return _fold_string(node.args[0], consts, hops)
    if isinstance(node, ast.Attribute) and node.attr in ("resolve", "absolute"):
        return _fold_string(node.value, consts, hops)
    return set()


def _basenames(node, consts):
    """Basenames a path expression could name; ``?`` stands for an unknown directory."""
    return {os.path.basename(p) for p in _fold_string(node, consts) if p}


def _mode_of(call):
    m = ""
    if len(call.args) >= 2:
        lit = _literal_str(call.args[1])
        if lit is not None:
            m = lit
    for kw in call.keywords or []:
        if kw.arg == "mode":
            lit = _literal_str(kw.value)
            if lit is not None:
                m = lit
    return m


def _is_write_mode(mode):
    return bool(set(mode or "") & set("wax+"))


# ---------------------------------------------------------------------------------------------
# the source-level census
# ---------------------------------------------------------------------------------------------
def _handle_open_sites(tree, consts):
    """``h = open(PATH, mode)`` -> {name: (path_node, mode, line)} plus context managers."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt, val = node.targets[0], node.value
            if isinstance(tgt, ast.Name) and isinstance(val, ast.Call) and \
                    _func_tail(val.func) in WRITE_HANDLE_CALLS and val.args:
                out[tgt.id] = (val.args[0], _mode_of(val), getattr(node, "lineno", 0))
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                call = item.context_expr
                if isinstance(call, ast.Call) and _func_tail(call.func) in WRITE_HANDLE_CALLS \
                        and call.args:
                    if isinstance(item.optional_vars, ast.Name):
                        out[item.optional_vars.id] = (
                            call.args[0], _mode_of(call), getattr(node, "lineno", 0))
    return out


def _bindings(tree):
    """Every ``NAME = <expr>`` in the source (last binding wins, which is what runs)."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name):
            out[node.targets[0].id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.value is not None:
            out[node.target.id] = node.value
    return out


def _reads_this_basename(expr, consts, binds, basename, hops=MAX_NAME_HOPS):
    """True when ``expr`` reads the published file back out (bytes or text)."""
    if isinstance(expr, ast.Call):
        tail = _func_tail(expr.func)
        if tail in ("read", "read_text", "read_bytes"):
            target = expr.func.value if isinstance(expr.func, ast.Attribute) else None
            if isinstance(target, ast.Call) and _func_tail(target.func) in WRITE_HANDLE_CALLS \
                    and target.args:
                if basename in _basenames(target.args[0], consts):
                    return True
                if _is_write_mode(_mode_of(target)):
                    return False
            if isinstance(target, ast.Name) and hops > 0:
                bound = binds.get(target.id)
                if bound is not None and _reads_this_basename(
                        bound, consts, binds, basename, hops - 1):
                    return True
                if target.id in binds and isinstance(bound, ast.Call) and \
                        _func_tail(bound.func) in WRITE_HANDLE_CALLS and bound.args:
                    return basename in _basenames(bound.args[0], consts)
        if tail in ("copyfile", "copy", "copy2") and len(expr.args) >= 2:
            return basename in _basenames(expr.args[0], consts)
    return False


def _classify_payload(node, consts, binds, basename, backups, hops=MAX_NAME_HOPS):
    """What does this expression put into the published file?"""
    if node is None:
        return P_UNKNOWN
    lit = _literal_str(node)
    if lit is not None:
        return P_EMPTY if lit.strip() == "" else P_CONSTRUCTED
    if isinstance(node, ast.Name):
        if node.id in backups:
            return P_BACKUP
        bound = binds.get(node.id)
        if bound is not None and hops > 0:
            if _reads_this_basename(bound, consts, binds, basename):
                return P_BACKUP
            return _classify_payload(bound, consts, binds, basename, backups, hops - 1)
        return P_UNKNOWN
    if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.DictComp, ast.ListComp)):
        return P_CONSTRUCTED
    if isinstance(node, ast.JoinedStr):
        return P_CONSTRUCTED
    if isinstance(node, ast.BinOp):
        return P_CONSTRUCTED
    if isinstance(node, ast.Call):
        tail = _func_tail(node.func)
        if tail in PAYLOAD_CALLS:
            return P_CONSTRUCTED
        if tail in ("read", "read_text", "read_bytes"):
            return P_BACKUP if _reads_this_basename(node, consts, binds, basename) else P_UNKNOWN
        if tail in ("encode", "decode", "strip", "replace", "sub", "join", "format_map"):
            return P_CONSTRUCTED
        if tail in ("copyfile", "copy", "copy2", "move", "replace", "rename") and len(node.args) >= 2:
            return P_BACKUP if basename in _basenames(node.args[0], consts) else P_COPIED
        if node.args:
            return _classify_payload(node.args[0], consts, binds, basename, backups, hops - 1)
        return P_UNKNOWN
    return P_UNKNOWN


def _finally_ranges(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and node.finalbody:
            lo = min(getattr(n, "lineno", 0) for n in node.finalbody)
            hi = max(getattr(n, "end_lineno", getattr(n, "lineno", 0)) for n in node.finalbody)
            out.append([lo, hi])
    return out


def write_sites(source_text, basename):
    """Every site in ``source_text`` that puts bytes on ``basename``, with its payload class.

    Independent of E492's recorded line numbers: the fold is redone here so a site the
    parent face missed shows up as a difference rather than as silence.
    """
    tree = ast.parse(source_text)
    consts = _collect_consts(tree)
    binds = _bindings(tree)
    handles = _handle_open_sites(tree, consts)
    finally_ranges = _finally_ranges(tree)

    # names bound to this face's own bytes
    backups = set()
    for name, value in binds.items():
        if _reads_this_basename(value, consts, binds, basename):
            backups.add(name)

    sites = []

    def add(line, payload, via, write_line=None, extra=None):
        rec = {
            "line": line,
            "write_call_line": write_line if write_line is not None else line,
            "via": via,
            "payload": payload,
            "sits_in_a_finally": any(lo <= line <= hi for lo, hi in finally_ranges) or any(
                lo <= (write_line if write_line is not None else line) <= hi
                for lo, hi in finally_ranges),
        }
        if extra:
            rec.update(extra)
        sites.append(rec)

    for node in ast.walk(tree):
        # handle.write(ARG) / handle.write_text(ARG)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                node.func.attr in WRITE_METHODS:
            target = node.func.value
            path_node = None
            mode = ""
            open_line = None
            if isinstance(target, ast.Call) and _func_tail(target.func) in WRITE_HANDLE_CALLS \
                    and target.args:
                path_node, mode = target.args[0], _mode_of(target)
                open_line = getattr(target, "lineno", 0)
            elif isinstance(target, ast.Name) and target.id in handles:
                path_node, mode, open_line = handles[target.id]
            if path_node is None:
                continue
            if basename not in _basenames(path_node, consts):
                continue
            payload = _classify_payload(
                node.args[0] if node.args else None, consts, binds, basename, backups)
            add(open_line or getattr(node, "lineno", 0), payload, "handle_write",
                write_line=getattr(node, "lineno", 0), extra={"mode": mode or "w"})
        # json.dump(OBJ, handle)
        if isinstance(node, ast.Call) and _func_tail(node.func) == "dump" and len(node.args) >= 2:
            fh = node.args[1]
            path_node = None
            open_line = None
            if isinstance(fh, ast.Name) and fh.id in handles:
                path_node = handles[fh.id][0]
                open_line = handles[fh.id][2]
            elif isinstance(fh, ast.Call) and fh.args and \
                    _func_tail(fh.func) in WRITE_HANDLE_CALLS:
                path_node = fh.args[0]
                open_line = getattr(fh, "lineno", 0)
            if path_node is None or basename not in _basenames(path_node, consts):
                continue
            payload = _classify_payload(node.args[0], consts, binds, basename, backups)
            add(open_line or getattr(node, "lineno", 0), payload, "json_dump",
                write_line=getattr(node, "lineno", 0))
        # copy / move families, destination is the second argument
        if isinstance(node, ast.Call):
            tail = _func_tail(node.func)
            if tail in COPY_CALLS + MOVE_CALLS and len(node.args) >= 2:
                if basename not in _basenames(node.args[1], consts):
                    continue
                payload = P_BACKUP if basename in _basenames(node.args[0], consts) else P_COPIED
                add(getattr(node, "lineno", 0), payload, "copy_call")

    sites.sort(key=lambda s: (s["line"], s["via"]))
    unique = []
    seen = set()
    for s in sites:
        key = (s["line"], s["via"], s["payload"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(s)
    return {
        "sites": unique,
        "backup_names": sorted(backups),
        "handle_count": len(handles),
        "folded_consts": len(consts),
    }


def class_of(sites):
    """The per-composer answer, from the site list alone."""
    authored = [s for s in sites if s["payload"] == P_CONSTRUCTED]
    restored = [s for s in sites if s["payload"] == P_BACKUP]
    if authored and restored:
        return C_AUTHORS_AND_RESTORES
    if authored:
        return C_AUTHORS_NO_RESTORE
    if restored:
        return C_BACKUP_ONLY
    return C_NEVER_WRITES


def read_basenames(source_text, published_basename):
    """Basenames this source opens for READING, other than the published one.

    Used to test the fair reading of an unrestored authored payload: a repair that
    re-publishes a mirror writes a document it built itself, but the document may be
    another file's payload plus a stamp -- which is a different claim from a fabrication.
    """
    tree = ast.parse(source_text)
    consts = _collect_consts(tree)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _func_tail(node.func) in WRITE_HANDLE_CALLS \
                and node.args:
            mode = _mode_of(node)
            if _is_write_mode(mode):
                continue
            for b in _basenames(node.args[0], consts):
                if b and b != published_basename:
                    out.add(b)
        if isinstance(node, ast.Call) and _func_tail(node.func) in ("load", "loads") and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Call) and _func_tail(arg.func) in WRITE_HANDLE_CALLS \
                    and arg.args and not _is_write_mode(_mode_of(arg)):
                for b in _basenames(arg.args[0], consts):
                    if b and b != published_basename:
                        out.add(b)
    return sorted(out)


def provenance_arm(face_rel, source_rel, source_text, basename):
    """Does the disk copy equal a file this source reads, once clock fields are removed?"""
    face_path = os.path.join(ROOT, face_rel)
    disk = _load_json(face_path)
    candidates = []
    for other in read_basenames(source_text, basename):
        hit = None
        for cand in (os.path.join(OUTDIR, other),
                     os.path.join(ROOT, "results", other),
                     os.path.join(ROOT, other)):
            if os.path.isfile(cand):
                hit = cand
                break
        if hit is None:
            candidates.append({"basename": other, "found": False, "same": False})
            continue
        try:
            other_doc = _load_json(hit)
            same = canon(other_doc) == canon(disk)
        except Exception:
            candidates.append({"basename": other, "found": True, "same": False,
                               "error": "unreadable"})
            continue
        candidates.append({"basename": other, "found": True, "same": same,
                           "path": _rel(hit)})
    return {
        "source": source_rel,
        "reads": [c["basename"] for c in candidates],
        "candidates": candidates,
        "matches_a_file_the_composer_reads": any(c["same"] for c in candidates),
    }


# ---------------------------------------------------------------------------------------------
# producer arm (reused from E493, which reused it from the disk-ownership card)
# ---------------------------------------------------------------------------------------------
CLOCK_KEYS = frozenset({
    "generated", "generated_at", "generated_utc", "elapsed", "elapsed_sec",
    "runtime_sec", "ts", "timestamp", "asof_runtime",
})


def canon(obj):
    if isinstance(obj, dict):
        return {k: canon(v) for k, v in obj.items() if k not in CLOCK_KEYS}
    if isinstance(obj, list):
        return [canon(x) for x in obj]
    return obj


def _import_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def producer_arm(producer_rel, face_rel, module_name):
    """Re-derive the producer's payload and compare the shape with the disk copy."""
    producer_path = os.path.join(ROOT, producer_rel)
    face_path = os.path.join(ROOT, face_rel)
    disk = _load_json(face_path)
    mod = _import_module(producer_path, module_name)
    built = None
    err = ""
    try:
        import inspect
        sig = inspect.signature(mod.build)
        cutoff = disk.get("evidence_cutoff")
        if "cutoff" in sig.parameters and cutoff:
            built = mod.build(cutoff)
        else:
            built = mod.build()
    except Exception as exc:
        err = "build failed: %s: %s" % (type(exc).__name__, str(exc)[:160])
    shape = verdict = payload = False
    if built is not None:
        try:
            shape = sorted(built.keys()) == sorted(disk.keys())
            verdict = built.get("verdict") == disk.get("verdict")
            payload = canon(built) == canon(disk)
        except Exception as exc:
            err = err or "compare failed: %s" % type(exc).__name__
    return {
        "producer": producer_rel,
        "build_error": err,
        "shape_matches_a_fresh_build": shape,
        "verdict_matches_a_fresh_build": verdict,
        "payload_re_derives_from_the_disk_copy": payload,
        "disk_sha16": _sha16(face_path) if os.path.isfile(face_path) else None,
    }


# ---------------------------------------------------------------------------------------------
# population
# ---------------------------------------------------------------------------------------------
def _newest(prefix):
    hits = sorted(p for p in os.listdir(OUTDIR)
                  if p.startswith(prefix) and p.endswith(".json"))
    if not hits:
        return None, []
    path = os.path.join(OUTDIR, hits[-1])
    return path, _load_json(path).get("rows") or []


def population():
    """E492's names, minus the ones E493 already answered -- both read, never restated."""
    src_path, rows = _newest(SOURCE_FACE_GLOB)
    prior_path, prior_rows = _newest(PRIOR_FACE_GLOB)
    already = {r.get("latest_basename") for r in prior_rows}
    kept = [r for r in rows if r.get("latest_basename") not in already]
    return src_path, kept, prior_path, sorted(already)


def build(do_producer=True):
    src_path, rows, prior_path, already = population()
    cache = {}
    measured = []
    for row in rows:
        basename = row.get("latest_basename")
        face_rel = row.get("published_path")
        extras = [e for e in (row.get("extras") or []) if e.get("role") in EXTRA_ROLES]
        composers = []
        for ex in extras:
            src_rel = ex.get("source")
            entry = {
                "source": src_rel,
                "role": ex.get("role"),
                "parent_discipline": ex.get("mutation_discipline"),
                "parent_saves_the_original_away_first": bool(
                    ex.get("saves_the_original_away_first")),
                "parent_write_site_count": ex.get("write_site_count"),
                "measured_sites": [],
                "class": C_NEVER_WRITES,
                "write_sites_i_find": 0,
                "write_site_count_agrees": None,
                "restore_disagreement": "",
                "parse_error": "",
                "payload_classes": [],
                "restores_the_face": False,
                "restore_sits_in_a_finally": False,
            }
            path = os.path.join(ROOT, src_rel or "")
            if not src_rel or not os.path.isfile(path):
                entry["parse_error"] = "source missing"
                composers.append(entry)
                continue
            if src_rel not in cache:
                with open(path, encoding="utf-8") as fh:
                    cache[src_rel] = fh.read()
            try:
                found = write_sites(cache[src_rel], basename)
            except SyntaxError as exc:
                entry["parse_error"] = "syntax error: %s" % str(exc)[:80]
                composers.append(entry)
                continue
            entry["measured_sites"] = found["sites"]
            entry["backup_names"] = found["backup_names"]
            entry["class"] = class_of(found["sites"])
            entry["payload_classes"] = sorted({s["payload"] for s in found["sites"]})
            entry["write_sites_i_find"] = len(found["sites"])
            entry["restores_the_face"] = any(s["payload"] == P_BACKUP for s in found["sites"])
            entry["restore_sits_in_a_finally"] = any(
                s["payload"] == P_BACKUP and s["sits_in_a_finally"] for s in found["sites"])
            # Reconcile against the parent's own numbers, not its line list: the parent
            # credits a write-mode open whether or not it is a write call, so a line diff
            # would report its bookkeeping as a disagreement.  Two claims are comparable --
            # how many write sites exist, and whether a restore exists at all.
            parent_count = entry["parent_write_site_count"]
            if isinstance(parent_count, int):
                entry["write_site_count_agrees"] = (parent_count == len(found["sites"]))
            parent_restore = entry["parent_discipline"] == D_PARENT_RESTORES
            if parent_restore != entry["restores_the_face"]:
                entry["restore_disagreement"] = (
                    "the_parent_lists_a_restore_and_this_build_finds_none"
                    if parent_restore else
                    "this_build_finds_a_restore_the_parent_does_not_list")
            composers.append(entry)

        authors = [c for c in composers if c["class"] == C_AUTHORS_NO_RESTORE]
        face_entry = {
            "latest_basename": basename,
            "published_path": face_rel,
            "extra_composers": len(composers),
            "composers": composers,
            "faces_class": C_NEVER_WRITES,
            "composers_that_author_a_payload": sum(
                1 for c in composers if c["class"] in (C_AUTHORS_AND_RESTORES, C_AUTHORS_NO_RESTORE)),
            "composers_that_author_without_a_restore": len(authors),
            "parses_now": False,
            "disk_sha16": None,
            "producer_arm": None,
            "provenance_arm": None,
        }
        if any(c["class"] == C_AUTHORS_NO_RESTORE for c in composers):
            face_entry["faces_class"] = C_AUTHORS_NO_RESTORE
        elif any(c["class"] == C_AUTHORS_AND_RESTORES for c in composers):
            face_entry["faces_class"] = C_AUTHORS_AND_RESTORES
        elif any(c["class"] == C_BACKUP_ONLY for c in composers):
            face_entry["faces_class"] = C_BACKUP_ONLY
        face_path = os.path.join(ROOT, face_rel or "")
        if face_rel and os.path.isfile(face_path):
            try:
                _load_json(face_path)
                face_entry["parses_now"] = True
            except Exception:
                face_entry["parses_now"] = False
            face_entry["disk_sha16"] = _sha16(face_path)
        if do_producer and authors and face_entry["parses_now"]:
            mod_name = "e494_producer_" + "".join(
                ch if ch.isalnum() else "_" for ch in (basename or "x"))[:40]
            face_entry["producer_arm"] = producer_arm(
                row.get("primary_composer_source"), face_rel, mod_name)
            for c in authors:
                if c["source"] not in cache:
                    continue
                face_entry["provenance_arm"] = provenance_arm(
                    face_rel, c["source"], cache[c["source"]], basename)
                break
        measured.append(face_entry)

    by_class = {}
    for f in measured:
        by_class[f["faces_class"]] = by_class.get(f["faces_class"], 0) + 1
    site_payloads = {}
    for f in measured:
        for c in f["composers"]:
            for s in c["measured_sites"]:
                site_payloads[s["payload"]] = site_payloads.get(s["payload"], 0) + 1

    authoring_composers = [c for f in measured for c in f["composers"]
                           if c["class"] in (C_AUTHORS_AND_RESTORES, C_AUTHORS_NO_RESTORE)]
    unrestored_composers = [c for f in measured for c in f["composers"]
                            if c["class"] == C_AUTHORS_NO_RESTORE]
    restored_composers = [c for f in measured for c in f["composers"]
                          if c["class"] == C_AUTHORS_AND_RESTORES]
    unrestored_faces = [f["latest_basename"] for f in measured
                        if f["faces_class"] == C_AUTHORS_NO_RESTORE]

    producer_shaped = [f["latest_basename"] for f in measured
                       if (f.get("producer_arm") or {}).get("shape_matches_a_fresh_build")
                       and (f.get("producer_arm") or {}).get("verdict_matches_a_fresh_build")]
    producer_failed = [f["latest_basename"] for f in measured
                       if (f.get("producer_arm") or {}).get("build_error")]

    summary = {
        "faces_examined": len(measured),
        "faces_in_source_population": len(measured) + len(already),
        "faces_excluded_as_already_measured": already,
        "source_face": _rel(src_path) if src_path else None,
        "prior_face": _rel(prior_path) if prior_path else None,
        "extra_composers_examined": sum(f["extra_composers"] for f in measured),
        "faces_by_class": by_class,
        "composers_that_author_a_payload": len(authoring_composers),
        "composers_that_author_and_restore": len(restored_composers),
        "composers_that_author_without_a_restore": len(unrestored_composers),
        "faces_with_an_unrestored_authoring_composer": len(unrestored_faces),
        "faces_with_a_restored_authoring_composer": sum(
            1 for f in measured if f["faces_class"] == C_AUTHORS_AND_RESTORES),
        "write_sites_by_payload": site_payloads,
        "write_sites_total": sum(site_payloads.values()),
        "sites_the_parent_face_missed": sum(
            max(0, c["write_sites_i_find"] - (c.get("parent_write_site_count") or 0))
            for f in measured for c in f["composers"]
            if isinstance(c.get("parent_write_site_count"), int)),
        "sites_the_parent_face_credited_that_are_not_write_calls": sum(
            max(0, (c.get("parent_write_site_count") or 0) - c["write_sites_i_find"])
            for f in measured for c in f["composers"]
            if isinstance(c.get("parent_write_site_count"), int)),
        "composers_whose_write_site_count_disagrees_with_the_parent": [
            {"face": f["latest_basename"], "source": c["source"],
             "parent": c.get("parent_write_site_count"), "here": c["write_sites_i_find"]}
            for f in measured for c in f["composers"]
            if c.get("write_site_count_agrees") is False],
        "restore_label_disagreements": [
            {"face": f["latest_basename"], "source": c["source"],
             "kind": c["restore_disagreement"]}
            for f in measured for c in f["composers"] if c["restore_disagreement"]],
        "sources_with_a_parse_error": sum(
            1 for f in measured for c in f["composers"] if c["parse_error"]),
        "faces_parseable_now": sum(1 for f in measured if f["parses_now"]),
        "producer_arms_run": sum(1 for f in measured if f["producer_arm"]),
        "provenance_arms_run": sum(1 for f in measured if f["provenance_arm"]),
        "unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads": sum(
            1 for f in measured
            if (f.get("provenance_arm") or {}).get("matches_a_file_the_composer_reads")),
        "unrestored_faces_whose_disk_copy_is_producer_shaped": len(producer_shaped),
        "unrestored_faces_whose_producer_build_failed": len(producer_failed),
    }
    return {
        "study": "E494_latest_authors",
        "card": CARD,
        "title": ("Do the other 49 multi-composed latest faces carry a composer that authors "
                  "a payload of its own, and how many of those writes have no restore in the "
                  "same source?"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "population_source": _rel(src_path) if src_path else None,
        "population_note": (
            "E492's multi-composed names minus the names E493 already answered; both lists are "
            "read from the newest parent faces, and the excluded names are published rather "
            "than dropped"),
        "classification_definition": {
            C_AUTHORS_AND_RESTORES: "a write of a payload this source builds, and a later write of the face's own saved bytes",
            C_AUTHORS_NO_RESTORE: "a write of a payload this source builds, and no write of the face's own bytes anywhere in the source",
            C_BACKUP_ONLY: "the source only ever puts the face's own saved bytes back",
            C_NEVER_WRITES: "no write site in this source names the published basename",
        },
        "payload_definition": {
            P_BACKUP: "the argument traces to a read of the same published file (or a copy of it)",
            P_CONSTRUCTED: "the argument is a serialisation, a literal, a string build, or a name bound to one",
            P_COPIED: "a copy/move whose source is a different basename",
            P_EMPTY: "an empty string literal",
            P_UNKNOWN: "the argument could not be traced within two name hops",
        },
        "rows": measured,
        "summary": summary,
        "verdict": None,
        "verdict_vocab": list(VERDICT_VOCAB),
        "card_answer": {
            "faces_with_a_composer_that_authors_a_payload": sum(
                1 for f in measured if f["composers_that_author_a_payload"]),
            "composers_that_author_a_payload": len(authoring_composers),
            "composers_that_author_with_restore": len(restored_composers),
            "composers_that_author_without_restore": len(unrestored_composers),
            "faces_with_an_unrestored_authoring_composer": unrestored_faces,
            "unrestored_faces_whose_disk_copy_is_producer_shaped": producer_shaped,
            "unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads": [
                f["latest_basename"] for f in measured
                if (f.get("provenance_arm") or {}).get("matches_a_file_the_composer_reads")],
            "unrestored_faces_with_an_unexplained_payload": [
                f["latest_basename"] for f in measured
                if f["faces_class"] == C_AUTHORS_NO_RESTORE
                and not (f.get("provenance_arm") or {}).get(
                    "matches_a_file_the_composer_reads")
                and not (f.get("producer_arm") or {}).get("shape_matches_a_fresh_build")],
        },
        "method_limits": [
            "the population is E492's 51 names minus E493's two; a harness E492 never found is outside this study",
            "authorship is decided from the source's own AST, so a payload built inside a helper this build does not follow is published as unclassifiable rather than as safe",
            "a name is traced through at most two hops, so a payload handed through three names reads as unclassifiable",
            "the producer arm answers shape and verdict, not bytes: a copy that is a stale vintage of its own producer still matches here",
            "the write forms recognised are handle writes, json.dump, and the copy/move families; a write performed by a subprocess or a library call inside another file is not seen",
        ],
    }


def verdict_for(rows, summary=None):
    rows = rows or []
    summary = summary or {}
    if not rows:
        return V_EMPTY
    if summary.get("sources_with_a_parse_error"):
        return V_ERROR
    examined = [c for f in rows for c in (f.get("composers") or [])]
    if not examined:
        return V_EMPTY
    if any(c["class"] == C_AUTHORS_NO_RESTORE for c in examined):
        return V_SOME_NO_RESTORE
    if any(c["class"] == C_AUTHORS_AND_RESTORES for c in examined):
        return V_ALL_RESTORE
    return V_NONE_AUTHOR


def tally_problems(face):
    """Re-derive every published number from the rows."""
    bad = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    ans = face.get("card_answer") or {}
    if face.get("card") != CARD:
        bad.append("the card id is not this study's")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("verdict outside the frozen vocabulary")
    if face.get("verdict") != verdict_for(rows, s):
        bad.append("the verdict does not re-derive from the rows")
    if s.get("faces_examined") != len(rows):
        bad.append("faces_examined does not equal the row count")
    if s.get("extra_composers_examined") != sum(
            len(f.get("composers") or []) for f in rows):
        bad.append("extra_composers_examined does not re-derive")
    if s.get("faces_in_source_population") != len(rows) + len(
            s.get("faces_excluded_as_already_measured") or []):
        bad.append("the source population is not rows plus the excluded names")
    by_class = {}
    for f in rows:
        by_class[f.get("faces_class")] = by_class.get(f.get("faces_class"), 0) + 1
    if (s.get("faces_by_class") or {}) != {k: v for k, v in by_class.items() if v}:
        bad.append("faces_by_class does not re-derive")
    site_payloads = {}
    for f in rows:
        for c in f.get("composers") or []:
            for st in c.get("measured_sites") or []:
                site_payloads[st.get("payload")] = site_payloads.get(st.get("payload"), 0) + 1
    if (s.get("write_sites_by_payload") or {}) != site_payloads:
        bad.append("write_sites_by_payload does not re-derive")
    if s.get("write_sites_total") != sum(site_payloads.values()):
        bad.append("write_sites_total does not re-derive")
    composers_for_recon = [c for f in rows for c in (f.get("composers") or [])]
    if s.get("sites_the_parent_face_missed") != sum(
            max(0, c["write_sites_i_find"] - (c.get("parent_write_site_count") or 0))
            for c in composers_for_recon
            if isinstance(c.get("parent_write_site_count"), int)):
        bad.append("sites_the_parent_face_missed does not re-derive")
    if s.get("sites_the_parent_face_credited_that_are_not_write_calls") != sum(
            max(0, (c.get("parent_write_site_count") or 0) - c["write_sites_i_find"])
            for c in composers_for_recon
            if isinstance(c.get("parent_write_site_count"), int)):
        bad.append("the credited-not-a-write-call tally does not re-derive")
    if sorted(d.get("source") for d in
              s.get("composers_whose_write_site_count_disagrees_with_the_parent") or []) != \
            sorted(c.get("source") for c in composers_for_recon
                   if c.get("write_site_count_agrees") is False):
        bad.append("the published write-site-count disagreements do not match the rows")
    if sorted((d.get("source"), d.get("kind")) for d in
              s.get("restore_label_disagreements") or []) != \
            sorted((c.get("source"), c["restore_disagreement"]) for c in composers_for_recon
                   if c.get("restore_disagreement")):
        bad.append("the published restore disagreements do not match the rows")
    composers = [c for f in rows for c in (f.get("composers") or [])]
    if s.get("provenance_arms_run") != sum(1 for f in rows if f.get("provenance_arm")):
        bad.append("provenance_arms_run does not re-derive")
    if len(ans.get("unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads") or []) != \
            s.get("unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads"):
        bad.append("the mirror-explained list and its count disagree")
    for name in ans.get("unrestored_faces_with_an_unexplained_payload") or []:
        row = next((f for f in rows if f.get("latest_basename") == name), None)
        if row is None:
            bad.append("an unexplained payload names a face that is not in the rows")
            continue
        if (row.get("provenance_arm") or {}).get("matches_a_file_the_composer_reads"):
            bad.append("face %s is called unexplained but its payload mirrors a read file"
                       % name)
        if (row.get("producer_arm") or {}).get("shape_matches_a_fresh_build"):
            bad.append("face %s is called unexplained but its producer re-derives" % name)
        if row.get("faces_class") != C_AUTHORS_NO_RESTORE:
            bad.append("face %s is unexplained without an unrestored authoring composer"
                       % name)
    if s.get("composers_that_author_without_a_restore") != sum(
            1 for c in composers if c.get("class") == C_AUTHORS_NO_RESTORE):
        bad.append("composers_that_author_without_a_restore does not re-derive")
    if s.get("composers_that_author_and_restore") != sum(
            1 for c in composers if c.get("class") == C_AUTHORS_AND_RESTORES):
        bad.append("composers_that_author_and_restore does not re-derive")
    if s.get("composers_that_author_a_payload") != (
            (s.get("composers_that_author_and_restore") or 0)
            + (s.get("composers_that_author_without_a_restore") or 0)):
        bad.append("the authoring composer tally is not the sum of its two classes")
    if ans.get("composers_that_author_a_payload") != s.get("composers_that_author_a_payload"):
        bad.append("the card answer's composer tally disagrees with the summary")
    if (ans.get("faces_with_an_unrestored_authoring_composer") or []) != [
            f.get("latest_basename") for f in rows
            if f.get("faces_class") == C_AUTHORS_NO_RESTORE]:
        bad.append("the named unrestored faces do not re-derive from the rows")
    if s.get("faces_with_an_unrestored_authoring_composer") != len(
            ans.get("faces_with_an_unrestored_authoring_composer") or []):
        bad.append("the unrestored face count and the named faces disagree")
    for f in rows:
        for c in f.get("composers") or []:
            if c.get("class") not in CLASS_VOCAB:
                bad.append("face %s carries a composer class outside the vocabulary"
                           % f.get("latest_basename"))
            for st in c.get("measured_sites") or []:
                if st.get("payload") not in PAYLOAD_VOCAB:
                    bad.append("face %s carries a payload class outside the vocabulary"
                               % f.get("latest_basename"))
            derived = class_of(c.get("measured_sites") or [])
            if derived != c.get("class"):
                bad.append("face %s composer %s: the class does not re-derive from its sites"
                           % (f.get("latest_basename"), c.get("source")))
            if c.get("class") == C_AUTHORS_NO_RESTORE and any(
                    st.get("payload") == P_BACKUP for st in c.get("measured_sites") or []):
                bad.append("face %s composer %s: credited as unrestored but a restore site exists"
                           % (f.get("latest_basename"), c.get("source")))
        if f.get("composers_that_author_without_a_restore") != sum(
                1 for c in f.get("composers") or []
                if c.get("class") == C_AUTHORS_NO_RESTORE):
            bad.append("face %s: the per-face unrestored count does not re-derive"
                       % f.get("latest_basename"))
        if f.get("faces_class") == C_AUTHORS_NO_RESTORE and not f.get(
                "composers_that_author_without_a_restore"):
            bad.append("face %s is classed as unrestored with no such composer"
                       % f.get("latest_basename"))
    if [r for r in rows if r.get("latest_basename") in SELF_EXCLUDED + (
            "latestauthors_latest.json",)]:
        bad.append("this study appears in its own population")
    return bad


def verify():
    return tally_problems(_load_json(os.path.join(OUTDIR, FACE_NAME)))


def _write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for p in (dated, os.path.join(OUTDIR, FACE_NAME)):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return dated


def cmd_run(do_producer=True):
    face = build(do_producer=do_producer)
    face["verdict"] = verdict_for(face["rows"], face["summary"])
    dated = _write(face)
    s = face["summary"]
    print("%s | %s" % (_rel(dated), face["verdict"]))
    print("faces %d (of %d) | extra composers %d | sites %d %s"
          % (s["faces_examined"], s["faces_in_source_population"],
             s["extra_composers_examined"], s["write_sites_total"],
             s["write_sites_by_payload"]))
    print("authoring composers %d (restore %d / no restore %d) | faces without a restore %d"
          % (s["composers_that_author_a_payload"], s["composers_that_author_and_restore"],
             s["composers_that_author_without_a_restore"],
             s["faces_with_an_unrestored_authoring_composer"]))
    print("parent reconciliation: this build finds %d write sites the parent does not count | "
          "%d parent write counts exceed what this build finds | count disagreements %d | "
          "restore disagreements %d"
          % (s["sites_the_parent_face_missed"],
             s["sites_the_parent_face_credited_that_are_not_write_calls"],
             len(s["composers_whose_write_site_count_disagrees_with_the_parent"]),
             len(s["restore_label_disagreements"])))
    print("producer arms %d | unrestored faces producer-shaped %d | build failures %d"
          % (s["producer_arms_run"],
             s["unrestored_faces_whose_disk_copy_is_producer_shaped"],
             s["unrestored_faces_whose_producer_build_failed"]))
    print("provenance arms %d | unrestored payloads that mirror a file their composer reads %d "
          "| unexplained %d"
          % (s["provenance_arms_run"],
             s["unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads"],
             len(face["card_answer"]["unrestored_faces_with_an_unexplained_payload"])))
    return 0


def cmd_check():
    problems = verify()
    for p in problems:
        print("PROBLEM:", p)
    print("check problems=%d" % len(problems))
    return 0 if not problems else 1


# ---------------------------------------------------------------------------------------------
# selftest -- fixtures only, no corpus walk
# ---------------------------------------------------------------------------------------------
S_CONSTRUCT_AND_RESTORE = '''
import io, json
FACE = os.path.join(OUTDIR, "x_latest.json")
def main():
    raw = io.open(FACE, "rb").read()
    doc = json.loads(raw.decode("utf-8"))
    doc["summary"]["n"] += 1
    body = json.dumps(doc, ensure_ascii=False)
    try:
        io.open(FACE, "w", encoding="utf-8").write(body)
        run()
    finally:
        io.open(FACE, "wb").write(raw)
'''

S_CONSTRUCT_LEAVE = '''
import io, json
FACE = os.path.join(OUTDIR, "x_latest.json")
def main():
    doc = {"rows": [], "summary": {"n": 1}}
    with open(FACE, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
'''

S_BACKUP_ONLY = '''
import io
FACE = os.path.join(OUTDIR, "x_latest.json")
def main():
    raw = io.open(FACE, "rb").read()
    io.open(FACE, "wb").write(raw)
'''

S_OTHER_FACE = '''
import io, json
OTHER = os.path.join(OUTDIR, "y_latest.json")
def main():
    open(OTHER, "w").write(json.dumps({"a": 1}))
'''

S_COPY_IN = '''
import shutil
FACE = os.path.join(OUTDIR, "x_latest.json")
SRC = os.path.join(OUTDIR, "z.json")
def main():
    shutil.copyfile(SRC, FACE)
'''

S_TWO_HOPS = '''
import io, json
FACE = os.path.join(OUTDIR, "x_latest.json")
def main():
    doc = build_doc()
    text = json.dumps(doc)
    body = text
    open(FACE, "w").write(body)
'''


def _row(basename, composers, faces_class=None):
    unrestored = sum(1 for c in composers if c["class"] == C_AUTHORS_NO_RESTORE)
    authored = sum(1 for c in composers
                   if c["class"] in (C_AUTHORS_AND_RESTORES, C_AUTHORS_NO_RESTORE))
    if faces_class is None:
        if unrestored:
            faces_class = C_AUTHORS_NO_RESTORE
        elif any(c["class"] == C_AUTHORS_AND_RESTORES for c in composers):
            faces_class = C_AUTHORS_AND_RESTORES
        elif any(c["class"] == C_BACKUP_ONLY for c in composers):
            faces_class = C_BACKUP_ONLY
        else:
            faces_class = C_NEVER_WRITES
    return {"latest_basename": basename, "published_path": "results/state_tilt/" + basename,
            "extra_composers": len(composers), "composers": composers,
            "faces_class": faces_class,
            "composers_that_author_a_payload": authored,
            "composers_that_author_without_a_restore": unrestored}


def _composer(source, sites, klass=None, parent_count=None, parent_restore=None):
    klass = klass or class_of(sites)
    restores = any(s["payload"] == P_BACKUP for s in sites)
    parent_count = len(sites) if parent_count is None else parent_count
    parent_restore = restores if parent_restore is None else parent_restore
    disagreement = ""
    if bool(parent_restore) != restores:
        disagreement = ("the_parent_lists_a_restore_and_this_build_finds_none"
                        if parent_restore else
                        "this_build_finds_a_restore_the_parent_does_not_list")
    return {"source": source, "role": R_HARNESS,
            "parent_write_site_count": parent_count,
            "parent_restore_call_lines": [1] if parent_restore else [],
            "measured_sites": sites, "class": klass,
            "write_sites_i_find": len(sites),
            "write_site_count_agrees": parent_count == len(sites),
            "restore_disagreement": disagreement,
            "parse_error": "", "payload_classes": sorted({s["payload"] for s in sites}),
            "restores_the_face": restores,
            "restore_sits_in_a_finally": any(
                s["payload"] == P_BACKUP and s["sits_in_a_finally"] for s in sites)}


def selftest():
    out = []

    def leg(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    got = write_sites(S_CONSTRUCT_AND_RESTORE, "x_latest.json")
    legs = class_of(got["sites"])
    leg("a harness that builds a payload and restores is classed as restoring", legs == C_AUTHORS_AND_RESTORES, legs)
    leg("the restore is recognised by name", got["backup_names"] == ["raw"], str(got["backup_names"]))
    leg("the restore is seen inside a finally",
        any(s["payload"] == P_BACKUP and s["sits_in_a_finally"] for s in got["sites"]))
    leg("the authored payload is the dumps name, not the literal",
        sum(1 for s in got["sites"] if s["payload"] == P_CONSTRUCTED) == 1,
        str([s["payload"] for s in got["sites"]]))
    leg("both writes land on the published basename through os.path.join",
        len({s["line"] for s in got["sites"]}) == 2, str([s["line"] for s in got["sites"]]))

    got = write_sites(S_CONSTRUCT_LEAVE, "x_latest.json")
    leg("json.dump into a with-handle is seen",
        class_of(got["sites"]) == C_AUTHORS_NO_RESTORE, class_of(got["sites"]))
    leg("a dict literal written through json.dump counts as constructed",
        [s["payload"] for s in got["sites"]] == [P_CONSTRUCTED], str(got["sites"]))

    got = write_sites(S_BACKUP_ONLY, "x_latest.json")
    leg("a source that only writes the face back is backup-only",
        class_of(got["sites"]) == C_BACKUP_ONLY, class_of(got["sites"]))

    got = write_sites(S_OTHER_FACE, "x_latest.json")
    leg("a write to another basename is not this face",
        class_of(got["sites"]) == C_NEVER_WRITES, str(got["sites"]))

    got = write_sites(S_COPY_IN, "x_latest.json")
    leg("a copy into the face from another path is copied, not authored",
        [s["payload"] for s in got["sites"]] == [P_COPIED], str(got["sites"]))
    leg("a copy from another path is not treated as a restore",
        class_of(got["sites"]) == C_NEVER_WRITES, class_of(got["sites"]))

    got = write_sites(S_TWO_HOPS, "x_latest.json")
    leg("a payload bound through two names is still traced",
        class_of(got["sites"]) == C_AUTHORS_NO_RESTORE, class_of(got["sites"]))

    # the class must re-derive from the published sites alone
    sites = [{"line": 1, "via": "handle_write", "payload": P_CONSTRUCTED,
              "sits_in_a_finally": False}]
    leg("class re-derives from a published site list (no restore)",
        class_of(sites) == C_AUTHORS_NO_RESTORE, class_of(sites))
    leg("class re-derives from a published site list (restore present)",
        class_of(sites + [{"line": 2, "via": "handle_write", "payload": P_BACKUP,
                           "sits_in_a_finally": True}]) == C_AUTHORS_AND_RESTORES)
    leg("an empty site list is never-writes", class_of([]) == C_NEVER_WRITES)

    # verdict from rows
    r_ok = _row("a_latest.json", [_composer("s.py", [
        {"line": 1, "via": "handle_write", "payload": P_CONSTRUCTED, "sits_in_a_finally": False},
        {"line": 2, "via": "handle_write", "payload": P_BACKUP, "sits_in_a_finally": True}])])
    r_bad = _row("b_latest.json", [_composer("t.py", [
        {"line": 3, "via": "handle_write", "payload": P_CONSTRUCTED, "sits_in_a_finally": False}])])
    leg("restoring composers give the all-restore verdict",
        verdict_for([r_ok], {"sources_with_a_parse_error": 0}) == V_ALL_RESTORE)
    leg("one unrestored authoring composer gives the no-restore verdict",
        verdict_for([r_ok, r_bad], {"sources_with_a_parse_error": 0}) == V_SOME_NO_RESTORE)
    leg("no authoring composer gives the none-author verdict",
        verdict_for([_row("c_latest.json", [_composer("u.py", [
            {"line": 1, "via": "handle_write", "payload": P_BACKUP,
             "sits_in_a_finally": False}])])],
            {"sources_with_a_parse_error": 0}) == V_NONE_AUTHOR)
    leg("an empty population is its own verdict", verdict_for([], {}) == V_EMPTY)
    leg("a parse error is not a clean result",
        verdict_for([r_ok], {"sources_with_a_parse_error": 1}) == V_ERROR)

    # a composer whose count or restore claim disagrees with the parent is a published
    # reconciliation, not silence
    c = _composer("v.py", [{"line": 9, "via": "handle_write", "payload": P_CONSTRUCTED,
                            "sits_in_a_finally": False}], parent_count=2)
    leg("a parent count above what this build finds is carried as a disagreement",
        c["write_site_count_agrees"] is False and c["write_sites_i_find"] == 1,
        str((c["parent_write_site_count"], c["write_sites_i_find"])))
    c2 = _composer("w.py", [{"line": 4, "via": "handle_write", "payload": P_CONSTRUCTED,
                             "sits_in_a_finally": False}], parent_restore=True)
    leg("a parent restore the site list does not contain is a disagreement",
        c2["restore_disagreement"] == "the_parent_lists_a_restore_and_this_build_finds_none",
        c2["restore_disagreement"])
    c3 = _composer("u.py", [{"line": 5, "via": "handle_write", "payload": P_CONSTRUCTED,
                             "sits_in_a_finally": False},
                            {"line": 6, "via": "handle_write", "payload": P_BACKUP,
                             "sits_in_a_finally": True}], parent_restore=False)
    leg("a restore this build finds and the parent does not list is a disagreement",
        c3["restore_disagreement"] == "this_build_finds_a_restore_the_parent_does_not_list",
        c3["restore_disagreement"])

    # the guard must reject a face whose class contradicts its own sites
    rows = [r_bad]
    face = {"card": CARD, "verdict": verdict_for(rows, {"sources_with_a_parse_error": 0}),
            "rows": rows,
            "summary": {"faces_examined": 1, "faces_in_source_population": 1,
                        "faces_excluded_as_already_measured": [],
                        "extra_composers_examined": 1,
                        "faces_by_class": {C_AUTHORS_NO_RESTORE: 1},
                        "composers_that_author_a_payload": 1,
                        "composers_that_author_and_restore": 0,
                        "composers_that_author_without_a_restore": 1,
                        "faces_with_an_unrestored_authoring_composer": 1,
                        "write_sites_by_payload": {P_CONSTRUCTED: 1},
                        "write_sites_total": 1,
                        "sources_with_a_parse_error": 0,
                        "sites_the_parent_face_missed": 0,
                        "sites_the_parent_face_credited_that_are_not_write_calls": 0,
                        "composers_whose_write_site_count_disagrees_with_the_parent": [],
                        "restore_label_disagreements": [],
                        "producer_arms_run": 0,
                        "provenance_arms_run": 0,
                        "unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads": 0,
                        "unrestored_faces_whose_disk_copy_is_producer_shaped": 0},
            "card_answer": {"composers_that_author_a_payload": 1,
                            "unrestored_faces_whose_payload_mirrors_a_file_its_composer_reads": [],
                            "unrestored_faces_with_an_unexplained_payload": ["b_latest.json"],
                            "faces_with_an_unrestored_authoring_composer": ["b_latest.json"]}}
    leg("a well-formed single-face payload passes its own guard", tally_problems(face) == [],
        str(tally_problems(face)))

    import copy
    f1 = copy.deepcopy(face)
    f1["rows"][0]["composers"][0]["class"] = C_AUTHORS_AND_RESTORES
    leg("a composer class that contradicts its sites is rejected", bool(tally_problems(f1)))
    f2 = copy.deepcopy(face)
    f2["summary"]["composers_that_author_without_a_restore"] = 0
    leg("an authoring tally that does not re-derive is rejected", bool(tally_problems(f2)))
    f3 = copy.deepcopy(face)
    f3["card_answer"]["faces_with_an_unrestored_authoring_composer"] = []
    leg("a named-face list that does not match the rows is rejected", bool(tally_problems(f3)))
    f4 = copy.deepcopy(face)
    f4["rows"][0]["faces_class"] = C_AUTHORS_AND_RESTORES
    leg("a face class that contradicts its composers is rejected", bool(tally_problems(f4)))
    f5 = copy.deepcopy(face)
    f5["verdict"] = V_ALL_RESTORE
    leg("a verdict that contradicts the rows is rejected", bool(tally_problems(f5)))
    f6 = copy.deepcopy(face)
    f6["summary"]["write_sites_by_payload"] = {P_CONSTRUCTED: 2}
    leg("a payload tally that does not re-derive is rejected", bool(tally_problems(f6)))
    f7 = copy.deepcopy(face)
    f7["card_answer"]["composers_that_author_a_payload"] = 2
    leg("a card answer that disagrees with the summary is rejected", bool(tally_problems(f7)))

    # self-exclusion
    f8 = copy.deepcopy(face)
    f8["rows"].append(_row("latestauthors_latest.json", []))
    f8["summary"]["faces_examined"] = 2
    f8["summary"]["faces_in_source_population"] = 2
    f8["summary"]["extra_composers_examined"] = 1
    f8["summary"]["faces_by_class"] = {C_AUTHORS_NO_RESTORE: 1, C_NEVER_WRITES: 1}
    leg("this study's own face in its population is rejected", bool(tally_problems(f8)))

    bad = [n for n, ok, d in out if not ok]
    for name, ok, detail in out:
        print(("PASS  " if ok else "FAIL  ") + name + ((" | " + detail) if detail and not ok else ""))
    print("selftest %d/%d" % (len(out) - len(bad), len(out)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E494 -- who authors a payload into a latest face")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "verify", "selftest", "build"])
    ap.add_argument("--no-producer", action="store_true",
                    help="skip the producer re-derivation arm for unrestored faces")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return cmd_run(do_producer=not args.no_producer)
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "verify":
        problems = verify()
        print("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if args.cmd == "build":
        face = build(do_producer=not args.no_producer)
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        print("verdict:", verdict_for(face["rows"], face["summary"]))
        return 0
    return selftest()


if __name__ == "__main__":
    sys.exit(main())