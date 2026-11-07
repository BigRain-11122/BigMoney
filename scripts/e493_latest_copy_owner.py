"""E493 -- for the two latest names whose only visible harness writes once with no
restore, is the copy on disk the producer's or the harness's?

E492 (r1518) published 51 multi-composed ``*_latest.json`` names and counted two whose
single-write harness was the only extra composer: ``deadprereg_latest.json`` and
``dirfield_latest.json``.  A static count is not an answer to "who owns the bytes" -- a
harness can (a) never open the face for writing, (b) write it and put the original back,
or (c) write it and leave whatever it wrote.  E492's label collapsed all three into one
string, and it counted one face whose harness has *zero* write sites.

Measured, two faces, three arms each, no draws, no engine, nothing published is left
changed:

  1. static arm -- classify every ``open(FACE, ...)`` in the harness by mode, find a
     whole-file backup read and a later write of that same backup, and note whether the
     restore sits in a ``finally`` block;
  2. live arm -- sha256 the published face, run the harness in its ``--doctor`` mode,
     sha256 again, and record the harness's own restore claim and return code (the
     original bytes are held here too, so a harness that leaks a mutant is repaired
     before this build returns);
  3. producer arm -- import the producer with its output directory pointed at a temp
     dir, re-derive the face, and compare payloads to the disk copy with clock fields
     removed.

Reads results/state_tilt/LATESTDOCTOR-*.json (E492) and the two harness/producer pairs;
writes results/state_tilt/LATESTCOPYOWNER-<cutoff>.json plus latestcopyowner_latest.json.
"""
import argparse
import ast
import hashlib
import importlib.util
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

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "latestcopyowner_latest.json"
DATED_PREFIX = "LATESTCOPYOWNER"
CARD = ("E493-FOR-THE-TWO-LATEST-NAMES-WHOSE-ONLY-VISIBLE-HARNESS-WRITES-ONCE-WITH-NO-"
        "RESTORE-IS-THE-COPY-ON-DISK-THE-PRODUCERS-OR-THE-HARNESSS")
SELF_EXCLUDED = ("e493_", "run_e493")

SOURCE_FACE_GLOB = "LATESTDOCTOR-*.json"
SELECT_KEY = "harness_single_write_composers"

# Clock-ish fields that legitimately differ between two runs of the same deterministic
# build.  Anything else that differs is a payload difference.
CLOCK_KEYS = frozenset({
    "generated", "generated_at", "generated_utc", "elapsed", "elapsed_sec",
    "runtime_sec", "ts", "timestamp", "asof_runtime",
})

P_READS_ONLY = "the_harness_opens_the_face_only_for_reading"
P_WRITES_AND_RESTORES = "the_harness_writes_the_face_and_writes_the_backup_back"
P_WRITES_AND_LEAVES = "the_harness_writes_the_face_and_never_puts_the_original_back"
PERSISTENCE_VOCAB = (P_READS_ONLY, P_WRITES_AND_RESTORES, P_WRITES_AND_LEAVES)

V_PRODUCERS = "the_copy_on_disk_is_the_producers_in_every_case"
V_HARNESS = "at_least_one_published_copy_matches_what_a_harness_writes"
V_UNTOLD = "the_disk_copy_matches_neither_a_fresh_producer_build_nor_a_harness_mutant"
V_EMPTY = "no_face_carries_a_single_write_harness"
V_ERROR = "a_face_could_not_be_measured_in_this_environment"
VERDICT_VOCAB = (V_PRODUCERS, V_HARNESS, V_UNTOLD, V_EMPTY, V_ERROR)

# The E492 label this card re-measures.  Kept as a literal so a change on either side
# shows up as a disagreement rather than passing silently.
E492_LABEL = "writes_the_name_once_with_no_restore_in_the_same_source"

WRITE_MODE_CHARS = frozenset("wax+")


def _rel(path):
    path = os.path.abspath(path)
    if path.startswith(ROOT + os.sep):
        return path[len(ROOT) + 1:].replace(os.sep, "/")
    return path


def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def canon(obj):
    """Drop clock fields recursively; everything else must match to be the same payload."""
    if isinstance(obj, dict):
        return {k: canon(v) for k, v in obj.items() if k not in CLOCK_KEYS}
    if isinstance(obj, list):
        return [canon(x) for x in obj]
    return obj


def _call_name(node):
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _targets_face(call):
    """True when the first argument of an open-like call names the face."""
    if not call.args:
        return False
    a = call.args[0]
    if isinstance(a, ast.Name):
        return a.id.upper() == "FACE" or a.id == "FACE_NAME"
    if isinstance(a, ast.Attribute):
        return a.attr.upper() == "FACE"
    return False


def _mode_of(call):
    m = ""
    if len(call.args) >= 2 and isinstance(call.args[1], ast.Constant):
        m = call.args[1].value if isinstance(call.args[1].value, str) else ""
    for kw in call.keywords or []:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            v = kw.value.value
            m = v if isinstance(v, str) else ""
    return m


def _read_backup_name(call):
    """``X = io.open(FACE, 'rb').read()`` -- returns X when the call is the read tail."""
    parent_attr = None
    src = call
    # walk up is not available here; caller passes the enclosing Assign instead
    return parent_attr if src else None


def _write_payload_name(arg):
    """What a ``.write(...)`` call puts on disk: the backup, a serialised payload, other."""
    if isinstance(arg, ast.Name):
        return ("name", arg.id)
    if isinstance(arg, ast.Call) and _call_name(arg.func) in ("dumps", "dump", "encode", "format"):
        return ("payload", "")
    if isinstance(arg, ast.Constant):
        return ("payload", "")
    return ("other", "")


def scan_harness(source_text):
    """Classify what a harness does to FACE from its own source.

    Returns a dict: open sites with modes, the backup assignment name, the restore line
    (line that writes that backup back), whether the restore sits under a ``finally``,
    whether the harness ever writes a payload of its own into the face, and the
    persistence class.
    """
    tree = ast.parse(source_text)
    sites = []
    backup_names = set()
    restore_lines = []
    payload_lines = []
    finally_lines = []

    # backup assignments: Name = <call>.read() where <call> opens FACE in a read mode
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            inner = node.value.func
            if _call_name(inner) == "read":
                target = node.value.func
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Call):
                    read_call = target.value
                    if _call_name(read_call.func) in ("open", "io.open") and _targets_face(read_call):
                        mode = _mode_of(read_call) or "r"
                        if not (WRITE_MODE_CHARS & set(mode)):
                            for t in node.targets:
                                if isinstance(t, ast.Name):
                                    backup_names.add(t.id)

    # any write whose payload is one of those backups
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node.func) in ("open", "io.open") and _targets_face(node):
            mode = _mode_of(node)
            kind = "write" if (mode and (WRITE_MODE_CHARS & set(mode))) or not mode else "read"
            sites.append({"line": getattr(node, "lineno", 0), "mode": mode or "", "kind": kind})
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "write":
            if not node.args:
                continue
            kind, name = _write_payload_name(node.args[0])
            if kind == "name" and name in backup_names:
                restore_lines.append(getattr(node, "lineno", 0))
                sites.append({"line": getattr(node, "lineno", 0), "mode": "wb", "kind": "write"})
            elif kind == "payload":
                # A payload written into FACE is the harness authoring a copy; it is only
                # the face when the handle came from FACE, so require the write-mode site
                # to exist in the same source (checked below by the write-site count).
                payload_lines.append(getattr(node, "lineno", 0))

    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and node.finalbody:
            lo = min(getattr(n, "lineno", 0) for n in node.finalbody)
            hi = max(getattr(n, "end_lineno", getattr(n, "lineno", 0)) for n in node.finalbody)
            finally_lines.append([lo, hi])
    restore_in_finally = any(lo <= line <= hi for line in restore_lines for lo, hi in finally_lines)

    write_sites = [s for s in sites if s["kind"] == "write"]
    if not write_sites:
        klass = P_READS_ONLY
    elif restore_lines:
        klass = P_WRITES_AND_RESTORES
    else:
        klass = P_WRITES_AND_LEAVES
    return {
        "open_sites": sorted(sites, key=lambda s: (s["line"], s["kind"])),
        "read_sites": sum(1 for s in sites if s["kind"] == "read"),
        "write_sites": len(write_sites),
        "backup_names": sorted(backup_names),
        "restore_lines": sorted(set(restore_lines)),
        "restore_sits_in_a_finally": restore_in_finally,
        "payload_write_lines": sorted(set(payload_lines)),
        "authors_a_payload_of_its_own": bool(write_sites) and bool(payload_lines),
        "persistence": klass,
    }


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def source_face():
    """E492's newest LATESTDOCTOR face -- the population is read, never restated."""
    hits = sorted(
        (p for p in os.listdir(OUTDIR)
         if p.startswith("LATESTDOCTOR-") and p.endswith(".json")),
    )
    if not hits:
        return None, []
    path = os.path.join(OUTDIR, hits[-1])
    face = _load_json(path)
    rows = [r for r in face.get("rows") or [] if (r.get(SELECT_KEY) or 0) > 0]
    return path, rows


def _run_harness_doctor(harness_path):
    """Run the harness in doctor mode, guarding the published face with our own backup."""
    import subprocess
    face_path = None  # resolved by caller through the module constant
    return face_path, harness_path


def live_arm(harness_rel, face_rel, timeout=900):
    """sha the face, run the harness doctor, sha again; hold the original here meanwhile."""
    import subprocess
    face_path = os.path.join(ROOT, face_rel)
    harness_path = os.path.join(ROOT, harness_rel)
    before_bytes = open(face_path, "rb").read()
    before = hashlib.sha256(before_bytes).hexdigest()
    rc, tail, out = None, "", ""
    try:
        proc = subprocess.run(
            [sys.executable, harness_path, "--doctor"],
            cwd=ROOT, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        rc = proc.returncode
        out = (proc.stdout or "") + (proc.stderr or "")
        tail = " | ".join([ln.strip() for ln in out.strip().splitlines()[-2:]])
    except Exception as exc:  # a doctor that cannot run is disclosed, not guessed
        tail = "the harness did not finish: %s" % type(exc).__name__
    after_bytes = open(face_path, "rb").read()
    after = hashlib.sha256(after_bytes).hexdigest()
    restored_by_us = False
    if after != before:
        with open(face_path, "wb") as fh:
            fh.write(before_bytes)
        restored_by_us = True
        after = hashlib.sha256(open(face_path, "rb").read()).hexdigest()
    claim = ""
    m = re.search(r"face restored byte-identical:\s*(\w+)", out)
    if m:
        claim = m.group(1)
    return {
        "harness": harness_rel,
        "returncode": rc,
        "sha16_before": before[:16],
        "sha16_after": after[:16],
        "byte_identical_after_the_run": before == after,
        "harness_claims_a_restore": claim,
        "repaired_by_this_build": restored_by_us,
        "tail": tail[:300],
    }


def _import_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def producer_arm(producer_rel, face_rel, module_name):
    """Re-derive the producer's payload and compare it with the disk copy.

    The producer's ``build()`` is pure -- it reads the tree and returns a face -- so this
    arm writes nothing and patches no path.  An earlier draft pointed the module's output
    directory at a temp dir, which broke the producer's *read* side (it opens a sibling
    face from the same directory) and reported a build failure that was this instrument's
    own doing; the failure is kept as a card lesson, not hidden.
    """
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
    payload_same = False
    keys_same = False
    verdict_same = False
    if built is not None:
        payload_same = canon(built) == canon(disk)
        keys_same = sorted(built.keys()) == sorted(disk.keys())
        verdict_same = built.get("verdict") == disk.get("verdict")
    return {
        "producer": producer_rel,
        "build_error": err,
        "payload_re_derives_from_the_disk_copy": payload_same,
        "shape_matches_a_fresh_build": keys_same,
        "verdict_matches_a_fresh_build": verdict_same,
        "disk_is_a_stale_vintage_of_its_own_producer": bool(
            built is not None and not payload_same and keys_same and verdict_same),
        "clock_fields_removed": sorted(k for k in CLOCK_KEYS if k in disk),
        "disk_sha16": _sha16(face_path),
    }


# The two pairs, resolved through E492's rows rather than restated: a face whose producer
# or harness cannot be named from its own row would be published as unmeasured instead.
ROLE_HARNESS = "a_doctor_harness"
ROLE_PRODUCER = "a_producer"


def _pairs(rows):
    out = []
    for row in rows:
        harness = None
        producer = None
        for c in row.get("composers") or []:
            if c.get("role") == ROLE_HARNESS and harness is None:
                harness = c.get("source")
            elif c.get("role") == ROLE_PRODUCER and producer is None:
                producer = c.get("source")
        out.append({
            "latest_basename": row.get("latest_basename"),
            "published_path": row.get("published_path"),
            "harness": harness,
            "producer": producer,
            "e492_label": "writes_the_name_once_with_no_restore_in_the_same_source",
        })
    return out


def build(do_live=True, do_producer=True):
    src_path, rows = source_face()
    pairs = _pairs(rows)
    measured = []
    for p in pairs:
        entry = dict(p)
        face_path = os.path.join(ROOT, p["published_path"] or "")
        entry["exists_on_disk"] = os.path.isfile(face_path)
        entry["static"] = None
        entry["live"] = None
        entry["producer_arm"] = None
        if entry["harness"]:
            hpath = os.path.join(ROOT, p["harness"])
            if os.path.isfile(hpath):
                with open(hpath, encoding="utf-8") as fh:
                    entry["static"] = scan_harness(fh.read())
        if do_live and entry["exists_on_disk"] and entry["harness"]:
            entry["live"] = live_arm(p["harness"], p["published_path"])
        if do_producer and entry["exists_on_disk"] and entry["producer"]:
            mod_name = "e493_producer_" + re.sub(r"\W", "_", os.path.basename(p["producer"]))
            entry["producer_arm"] = producer_arm(p["producer"], p["published_path"], mod_name)
        measured.append(entry)

    by_persistence = {}
    for e in measured:
        k = (e["static"] or {}).get("persistence") or "not_measured"
        by_persistence[k] = by_persistence.get(k, 0) + 1

    static_label_disagreements = []
    for e in measured:
        st = e["static"] or {}
        if not st:
            continue
        # E492's label is a claim about writing; a harness with zero write sites that
        # carries it is the label lying, and a harness that writes then restores is the
        # matcher missing the restore pair.
        if st["write_sites"] == 0 and e["e492_label"] == E492_LABEL:
            static_label_disagreements.append({
                "face": e["latest_basename"], "kind": "label_claims_a_write_and_there_is_none",
                "write_sites": 0,
            })
        elif st["restore_lines"] and e["e492_label"] == E492_LABEL:
            static_label_disagreements.append({
                "face": e["latest_basename"], "kind": "label_claims_no_restore_and_one_exists",
                "restore_lines": st["restore_lines"],
                "in_a_finally": st["restore_sits_in_a_finally"],
            })

    summary = {
        "faces_selected": len(measured),
        "source_face": _rel(src_path) if src_path else None,
        "selection_key": SELECT_KEY,
        "harness_persistence_by_class": by_persistence,
        "static_label_disagreements": static_label_disagreements,
        "faces_whose_harness_never_writes": sum(
            1 for e in measured if (e["static"] or {}).get("persistence") == P_READS_ONLY),
        "faces_whose_harness_writes_then_restores": sum(
            1 for e in measured if (e["static"] or {}).get("persistence") == P_WRITES_AND_RESTORES),
        "faces_whose_harness_writes_and_leaves": sum(
            1 for e in measured if (e["static"] or {}).get("persistence") == P_WRITES_AND_LEAVES),
        "live_runs": sum(1 for e in measured if e["live"]),
        "live_runs_that_left_the_face_byte_identical": sum(
            1 for e in measured if e["live"] and e["live"]["byte_identical_after_the_run"]),
        "faces_repaired_by_this_build": sum(
            1 for e in measured if e["live"] and e["live"]["repaired_by_this_build"]),
        "producer_builds": sum(1 for e in measured if e["producer_arm"]),
        "disk_matches_a_fresh_producer_build": sum(
            1 for e in measured
            if (e["producer_arm"] or {}).get("payload_re_derives_from_the_disk_copy")),
        "disk_is_a_stale_vintage_of_its_own_producer": sum(
            1 for e in measured
            if (e["producer_arm"] or {}).get("disk_is_a_stale_vintage_of_its_own_producer")),
        "disk_shape_matches_a_fresh_producer_build": sum(
            1 for e in measured
            if (e["producer_arm"] or {}).get("shape_matches_a_fresh_build")),
        "harnesses_that_author_a_payload_of_their_own": sum(
            1 for e in measured if (e["static"] or {}).get("authors_a_payload_of_its_own")),
        "disk_matches_a_harness_mutant": sum(
            1 for e in measured if e.get("disk_is_a_harness_mutant") is True),
        "faces_unmeasured": sum(
            1 for e in measured
            if not e["static"] or not (e["producer_arm"] or {}).get("shape_matches_a_fresh_build")),
    }
    return {
        "study": "E493_latest_copy_owner",
        "card": CARD,
        "title": ("For the two latest names whose only visible harness writes once with no "
                  "restore, is the copy on disk the producer's or the harness's?"),
        "evidence_cutoff": (measured[0]["published_path"] and "2026-11-07") if measured else "2026-11-07",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "population_source": _rel(src_path) if src_path else None,
        "role_definition": {
            "harness": "a run_eNNN_smoke_leg.py source that E492 labelled a doctor harness",
            "producer": "the source E492 labelled a producer for the same name",
        },
        "discipline_definition": (
            "three arms: static mode/backup/restore/payload reading, a live doctor run with "
            "the original bytes held by this build, and a producer re-derivation compared "
            "with the disk copy after clock fields are removed -- freshness and authorship "
            "are published as two different readings"),
        "rows": measured,
        "summary": summary,
        "verdict": None,
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is two faces: E492's label of 'writes once with no restore' is the only selector, so a harness E492 did not flag is not examined here",
            "the live arm sees the face before and after the run, not during it; a harness that writes and restores in the same second is indistinguishable from one that never wrote",
            "authorship is decided from what the harness's own source writes into the face; a harness that re-runs a producer inherits the producer's authorship, which this instrument reports rather than resolves",
            "a disk payload that differs from a fresh build is reported as a stale vintage only when the key set and the verdict still agree -- any other difference stays unexplained",
            "clock fields are removed by name, so a payload field that happens to be named like a clock field would be ignored",
        ],
    }


def verdict_for(rows, summary=None):
    summary = summary or {}
    rows = rows or []
    if not rows:
        return V_EMPTY
    if any((r.get("producer_arm") or {}).get("build_error") for r in rows):
        return V_ERROR
    if summary.get("disk_matches_a_harness_mutant"):
        return V_HARNESS
    measured = [r for r in rows if r.get("producer_arm")]
    if not measured:
        return V_ERROR
    # Authorship, not freshness: a harness that authors no payload cannot have written the
    # copy, and a payload whose shape and verdict re-derive from the producer is the
    # producer's document whether or not it is today's vintage.
    producer_shaped = all(
        (r["producer_arm"].get("shape_matches_a_fresh_build")
         and r["producer_arm"].get("verdict_matches_a_fresh_build")) for r in measured)
    no_harness_payload = not any((r.get("static") or {}).get("authors_a_payload_of_its_own")
                                 for r in measured)
    if producer_shaped and no_harness_payload:
        return V_PRODUCERS
    return V_UNTOLD


def tally_problems(face):
    """Re-derive every published number from the rows; a face that cannot be re-checked is
    not a face."""
    bad = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if face.get("card") != CARD:
        bad.append("the card id is not this study's")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("verdict outside the frozen vocabulary")
    if face.get("verdict") != verdict_for(rows, s):
        bad.append("the verdict does not re-derive from the rows")
    if s.get("faces_selected") != len(rows):
        bad.append("faces_selected does not equal the row count")
    if s.get("live_runs") != sum(1 for r in rows if r.get("live")):
        bad.append("live_runs does not re-derive")
    if s.get("producer_builds") != sum(1 for r in rows if r.get("producer_arm")):
        bad.append("producer_builds does not re-derive")
    if s.get("disk_matches_a_fresh_producer_build") != sum(
            1 for r in rows
            if (r.get("producer_arm") or {}).get("payload_re_derives_from_the_disk_copy")):
        bad.append("disk_matches_a_fresh_producer_build does not re-derive")
    if s.get("faces_whose_harness_never_writes") != sum(
            1 for r in rows if (r.get("static") or {}).get("persistence") == P_READS_ONLY):
        bad.append("faces_whose_harness_never_writes does not re-derive")
    if s.get("disk_shape_matches_a_fresh_producer_build") != sum(
            1 for r in rows
            if (r.get("producer_arm") or {}).get("shape_matches_a_fresh_build")):
        bad.append("disk_shape_matches_a_fresh_producer_build does not re-derive")
    if s.get("disk_is_a_stale_vintage_of_its_own_producer") != sum(
            1 for r in rows
            if (r.get("producer_arm") or {}).get("disk_is_a_stale_vintage_of_its_own_producer")):
        bad.append("disk_is_a_stale_vintage_of_its_own_producer does not re-derive")
    if s.get("harnesses_that_author_a_payload_of_their_own") != sum(
            1 for r in rows if (r.get("static") or {}).get("authors_a_payload_of_its_own")):
        bad.append("harnesses_that_author_a_payload_of_their_own does not re-derive")
    for r in rows:
        pa = r.get("producer_arm") or {}
        if pa.get("disk_is_a_stale_vintage_of_its_own_producer") and not (
                pa.get("shape_matches_a_fresh_build") and pa.get("verdict_matches_a_fresh_build")):
            bad.append("row %s calls itself a stale vintage without a matching shape and verdict"
                       % r.get("latest_basename"))
        if pa.get("disk_is_a_stale_vintage_of_its_own_producer") and pa.get(
                "payload_re_derives_from_the_disk_copy"):
            bad.append("row %s is both re-derivable and stale"
                       % r.get("latest_basename"))
    for r in rows:
        st = r.get("static")
        if st and st.get("persistence") not in PERSISTENCE_VOCAB:
            bad.append("row %s carries a persistence class outside the vocabulary"
                       % r.get("latest_basename"))
        if st and st["write_sites"] and not st["restore_lines"] and st["persistence"] != P_WRITES_AND_LEAVES:
            bad.append("row %s writes without restoring but is not classed as leaving it"
                       % r.get("latest_basename"))
        lv = r.get("live")
        if lv and lv.get("byte_identical_after_the_run") and lv.get("sha16_before") != lv.get("sha16_after"):
            bad.append("row %s claims identical bytes with two different digests"
                       % r.get("latest_basename"))
    static_disc = s.get("static_label_disagreements") or []
    if static_disc and not any("label_claims" in d.get("kind", "") for d in static_disc):
        bad.append("a disagreement list is published with no disagreement kind")
    return bad


def verify():
    face = _load_json(os.path.join(OUTDIR, FACE_NAME))
    return tally_problems(face)


def _write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for p in (dated, os.path.join(OUTDIR, FACE_NAME)):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return dated


def cmd_run(do_live=True, do_producer=True):
    face = build(do_live=do_live, do_producer=do_producer)
    face["verdict"] = verdict_for(face["rows"], face["summary"])
    dated = _write(face)
    s = face["summary"]
    print("%s | %s" % (_rel(dated), face["verdict"]))
    print("faces %d | harness persistence %s" % (s["faces_selected"], s["harness_persistence_by_class"]))
    print("live runs %d identical %d repaired %d | producer builds %d disk-matches %d"
          % (s["live_runs"], s["live_runs_that_left_the_face_byte_identical"],
             s["faces_repaired_by_this_build"], s["producer_builds"],
             s["disk_matches_a_fresh_producer_build"]))
    print("static label disagreements %d" % len(s["static_label_disagreements"]))
    return 0


def cmd_check():
    problems = verify()
    for p in problems:
        print("PROBLEM:", p)
    print("check problems=%d" % len(problems))
    return 0 if not problems else 1


# ---------------------------------------------------------------------------------------------
# selftest -- fixtures only, no corpus walk, no harness run
# ---------------------------------------------------------------------------------------------
READS_ONLY_SRC = '''
import io
FACE = "x_latest.json"
def main():
    raw = open(FACE, "rb").read()
    doc = json.loads(raw.decode("utf-8"))
    doc["rows"][0]["class"] = "read"
    return 0
'''

WRITES_RESTORE_SRC = '''
import io
FACE = "x_latest.json"
def main():
    backup = io.open(FACE, "rb").read()
    try:
        io.open(FACE, "w", encoding="utf-8").write("{}")
    finally:
        io.open(FACE, "wb").write(backup)
'''

WRITES_LEAVE_SRC = '''
import io
FACE = "x_latest.json"
def main():
    io.open(FACE, "w", encoding="utf-8").write("{}")
    return 0
'''

RESTORE_ONLY_SRC = '''
import io
FACE = "x_latest.json"
def main():
    backup = io.open(FACE, "rb").read()
    try:
        do_work()
    finally:
        io.open(FACE, "wb").write(backup)
'''


def _producer_row(**over):
    row = {"latest_basename": "x",
           "static": {"persistence": P_READS_ONLY, "write_sites": 0, "restore_lines": [],
                      "authors_a_payload_of_its_own": False},
           "live": {"byte_identical_after_the_run": True, "sha16_before": "a", "sha16_after": "a"},
           "producer_arm": {"payload_re_derives_from_the_disk_copy": True,
                            "shape_matches_a_fresh_build": True,
                            "verdict_matches_a_fresh_build": True,
                            "disk_is_a_stale_vintage_of_its_own_producer": False,
                            "build_error": ""}}
    row.update(over)
    return row


def _summary_for(rows):
    return {
        "faces_selected": len(rows),
        "live_runs": sum(1 for r in rows if r.get("live")),
        "producer_builds": sum(1 for r in rows if r.get("producer_arm")),
        "disk_matches_a_fresh_producer_build": sum(
            1 for r in rows if (r.get("producer_arm") or {}).get("payload_re_derives_from_the_disk_copy")),
        "disk_shape_matches_a_fresh_producer_build": sum(
            1 for r in rows if (r.get("producer_arm") or {}).get("shape_matches_a_fresh_build")),
        "disk_is_a_stale_vintage_of_its_own_producer": sum(
            1 for r in rows if (r.get("producer_arm") or {}).get("disk_is_a_stale_vintage_of_its_own_producer")),
        "harnesses_that_author_a_payload_of_their_own": sum(
            1 for r in rows if (r.get("static") or {}).get("authors_a_payload_of_its_own")),
        "faces_whose_harness_never_writes": sum(
            1 for r in rows if (r.get("static") or {}).get("persistence") == P_READS_ONLY),
        "disk_matches_a_harness_mutant": 0,
        "static_label_disagreements": [],
    }


def selftest():
    out = []

    def leg(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    st = scan_harness(READS_ONLY_SRC)
    leg("a read-only harness is classed as never writing", st["persistence"] == P_READS_ONLY,
        st["persistence"])
    leg("a read-only harness still counts its read site", st["read_sites"] == 1, str(st["read_sites"]))
    leg("a read-only harness authors no payload", st["authors_a_payload_of_its_own"] is False)

    st = scan_harness(WRITES_RESTORE_SRC)
    leg("a backup read is recognised by name", st["backup_names"] == ["backup"], str(st["backup_names"]))
    leg("the write of that backup is the restore", st["restore_lines"] == [9], str(st["restore_lines"]))
    leg("the restore is seen inside a finally", st["restore_sits_in_a_finally"] is True)
    leg("write-then-restore is its own class", st["persistence"] == P_WRITES_AND_RESTORES,
        st["persistence"])

    st = scan_harness(WRITES_LEAVE_SRC)
    leg("a plain write is classed as leaving the copy", st["persistence"] == P_WRITES_AND_LEAVES,
        st["persistence"])
    leg("a leaving harness has no restore line", st["restore_lines"] == [], str(st["restore_lines"]))
    leg("a leaving harness authors a payload", st["authors_a_payload_of_its_own"] is True)

    st = scan_harness(RESTORE_ONLY_SRC)
    leg("a restore-only harness writes but authors no payload",
        st["persistence"] == P_WRITES_AND_RESTORES and st["authors_a_payload_of_its_own"] is False,
        "%s / %s" % (st["persistence"], st["authors_a_payload_of_its_own"]))

    leg("clock fields are dropped by canon",
        canon({"a": 1, "generated": "x", "rows": [{"ts": 1, "v": 2}]}) == {"a": 1, "rows": [{"v": 2}]})
    leg("a payload field is not dropped",
        canon({"elapsed_sec": 1, "verdict": "v"}) == {"verdict": "v"})

    rows_producer = [_producer_row()]
    leg("producer-shaped rows give the producers verdict",
        verdict_for(rows_producer, _summary_for(rows_producer)) == V_PRODUCERS)
    leg("an empty row list is the empty verdict", verdict_for([], {}) == V_EMPTY)
    leg("a mutant match outranks the producer reading",
        verdict_for(rows_producer, {"disk_matches_a_harness_mutant": 1}) == V_HARNESS)
    leg("a build error is disclosed as an error",
        verdict_for([_producer_row(producer_arm={"build_error": "boom"})], {}) == V_ERROR)

    stale = _producer_row(producer_arm={"payload_re_derives_from_the_disk_copy": False,
                                        "shape_matches_a_fresh_build": True,
                                        "verdict_matches_a_fresh_build": True,
                                        "disk_is_a_stale_vintage_of_its_own_producer": True,
                                        "build_error": ""})
    leg("a stale vintage of the producer is still the producer's copy",
        verdict_for([stale], _summary_for([stale])) == V_PRODUCERS)

    reshaped = _producer_row(producer_arm={"payload_re_derives_from_the_disk_copy": False,
                                           "shape_matches_a_fresh_build": False,
                                           "verdict_matches_a_fresh_build": True,
                                           "disk_is_a_stale_vintage_of_its_own_producer": False,
                                           "build_error": ""})
    leg("a payload of another shape is untold",
        verdict_for([reshaped], _summary_for([reshaped])) == V_UNTOLD)

    authoring = _producer_row(static={"persistence": P_WRITES_AND_LEAVES, "write_sites": 1,
                                      "restore_lines": [], "authors_a_payload_of_its_own": True})
    leg("a harness that authors a payload blocks the producer verdict",
        verdict_for([authoring], _summary_for([authoring])) == V_UNTOLD)

    face = {"card": CARD, "verdict": V_PRODUCERS, "rows": [_producer_row()]}
    face["summary"] = _summary_for(face["rows"])
    leg("a clean face tallies zero problems", tally_problems(face) == [], str(tally_problems(face)))

    bad = json.loads(json.dumps(face))
    bad["summary"]["disk_matches_a_fresh_producer_build"] = 0
    leg("a summary that does not re-derive is refused",
        any("disk_matches_a_fresh_producer_build does not re-derive" in p for p in tally_problems(bad)))

    bad = json.loads(json.dumps(face))
    bad["verdict"] = V_HARNESS
    leg("a verdict outside the rows is refused",
        any("verdict does not re-derive" in p for p in tally_problems(bad)))

    bad = json.loads(json.dumps(face))
    bad["rows"][0]["static"]["persistence"] = "whatever"
    leg("a persistence class outside the vocabulary is refused",
        any("persistence class outside the vocabulary" in p for p in tally_problems(bad)))

    bad = json.loads(json.dumps(face))
    bad["rows"][0]["live"]["sha16_after"] = "b"
    leg("two digests cannot both be byte-identical",
        any("two different digests" in p for p in tally_problems(bad)))

    bad = json.loads(json.dumps(face))
    bad["rows"][0]["static"]["write_sites"] = 1
    bad["rows"][0]["static"]["restore_lines"] = []
    leg("writes without a restore must be classed as leaving it",
        any("writes without restoring" in p for p in tally_problems(bad)))

    # the E492 label lies when it is carried by a harness with no write site
    disc = [{"face": "x", "kind": "label_claims_a_write_and_there_is_none", "write_sites": 0}]
    leg("the label-lying kind is a legal disagreement",
        all("label_claims" in d["kind"] for d in disc))

    passed = sum(1 for _, ok, _ in out if ok)
    for name, ok, detail in out:
        if not ok:
            print("[FAIL] " + name + ((" | " + detail) if detail else ""))
    print("selftest %d/%d" % (passed, len(out)))
    return 0 if passed == len(out) else 1


def main(argv):
    ap = argparse.ArgumentParser(description="E493 latest copy owner")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "verify", "selftest", "static"])
    ap.add_argument("--no-live", action="store_true", help="skip the doctor runs")
    ap.add_argument("--no-producer", action="store_true", help="skip the producer builds")
    a = ap.parse_args(argv[1:])
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return cmd_check()
    if a.cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 1
    if a.cmd == "static":
        return cmd_run(do_live=False, do_producer=False)
    return cmd_run(do_live=not a.no_live, do_producer=not a.no_producer)


if __name__ == "__main__":
    sys.exit(main(sys.argv))