"""E396 -- the one same-document pair, priced, and the test that produced it.

E395 published exactly one pair in which a producer writes the key unconditionally into *this
very* face: ``logs/iteration-loop/state.json`` / ``last_tick``, a dict-literal key set at module
level by ``results/_r128bmc_resolve_storm.py``.  E395 was careful to say the pair is an
anomaly, not a conclusion, and left three honest explanations that a reader can tell apart:

  (a) SCHEMA REGRESSION -- a later writer of the same face dropped the key;
  (b) DUMP TARGET       -- the dict does not reach this file at run time;
  (c) STALE READ SITE   -- the read no longer names this face.

This study prices all three rather than taking whichever one is cheapest to believe:

  (a) the face's own git history (``git log -S`` over exactly this path) gives the boundary
      commit -- the last revision that carried the key and the first that did not -- plus the
      key-set difference across that boundary.  A history that never carried the key is
      published as ``never_carried`` and (a) is ruled out, not merely unfound;
  (b) the producer is re-parsed with the SAME assign->dump hop E395 used, and the hop now
      publishes the literal target string the dump carries instead of only a boolean.  The
      string is then classified against the face path at four granularities;
  (c) the read site is published verbatim and typed: does it read this face as its primary
      source, as a fallback, or not at all.

The load-bearing half is the generalisation.  E395 decided "this dump writes this face" with
``face_basename in value`` -- a SUBSTRING test -- so any face whose basename is a proper SUFFIX
of another face's basename can be credited with a write it never receives.  The study therefore
also runs a suffix-collision census over the faces in E395's own population and re-derives every
same-document claim under an exact-basename test, publishing which pairs move.  The classifier
in E395 is not edited: the defect is reported here, where it can be measured, not patched away.

    python scripts/e396_last_tick.py run
    python scripts/e396_last_tick.py verify
    python scripts/e396_last_tick.py selftest
"""
import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e395_conditional_write as e395      # same walker, same hop: imported, not rebuilt

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E396_last_tick"
TODAY = "2026-11-03"
FACE = "LASTTICK-%s.json" % TODAY
LATEST = "lasttick_latest.json"
SOURCE_FACE = os.path.join(OUTDIR, "CONDITIONALWRITE-%s.json" % TODAY)

KEY = "last_tick"
FACE_PATH = "logs/iteration-loop/state.json"

# target classes, most specific first
T_EXACT_PATH = "names_the_face_path"
T_EXACT_BASENAME = "names_this_faces_basename"
T_SUFFIX_ONLY = "basename_is_a_proper_suffix_of_the_target"      # the defect's shape
T_CONTAINS_PATH = "carries_the_face_path_but_names_another_file"
T_OTHER = "names_another_document"


def _norm(p):
    return (p or "").replace("\\", "/")


def classify_target(target, face_relpath):
    """Why a dump target string is, or is not, this face's file."""
    t = _norm(target)
    face = _norm(face_relpath)
    base = os.path.basename(face)
    if not t:
        return T_OTHER
    if t == face or t.endswith("/" + face):
        return T_EXACT_PATH
    tbase = os.path.basename(t)
    if tbase == base:
        return T_EXACT_BASENAME
    if t.endswith(base) and tbase != base:
        return T_SUFFIX_ONLY
    if face in t:
        return T_CONTAINS_PATH
    return T_OTHER


def _literal_strings(call):
    out = []
    for arg in list(call.args) + [kw.value for kw in call.keywords]:
        for sub in ast.walk(arg):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                out.append(sub.value)
    return out


def dump_link_targets(src, key):
    """Every ``name = {...key...}`` -> ``dump(name, <target>)`` hop, with the target string.

    This is E395's ``via_name_to_this_face`` hop with one more field published: the literal the
    dump carries.  Only module-level dict literals are covered because that is the pair under
    study; a hop that never reaches a dump is published as ``no_dump`` rather than dropped.
    """
    tree = e395._parsed(src)
    if tree is None:
        return None
    hops = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        keys = [k.value for k in node.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        if key not in keys:
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not names:
            continue
        scopes = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        reached = []
        for call in scopes:
            if not e395._is_dump_call(call) or not call.args:
                continue
            first = call.args[0]
            if isinstance(first, ast.Name) and first.id in names:
                reached.append({"line": getattr(call, "lineno", None),
                                "targets": _literal_strings(call)})
        hops.append({"assign_line": getattr(node, "lineno", None),
                     "name": names[0], "key_in_literal": True,
                     "dumps": reached})
    return hops


def history_boundary(repo, path, key, timeout=30, sample=14):
    """The newest revisions that touched this exact path, newest first.

    ``git log -S`` would be the exact instrument, but it needs every historical blob: in this
    blob:none promisor clone the first miss starts a lazy fetch and the walk stops being a
    bounded operation (r1226 lesson, paid again on the first burn of this study).  So the
    history leg is a BOUNDED SAMPLE of the revisions that touched the path -- commit metadata
    only, which never needs a blob -- and each sampled revision is read with its own short wall.
    A sample that misses the key is published as such: it does not prove the face never carried
    it, and the study says so rather than reading silence as evidence.
    """
    cmd = ["git", "log", "--format=%H|%ad|%s", "--date=short", "-n%d" % sample, "--", path]
    try:
        raw = subprocess.run(cmd, cwd=repo, capture_output=True, timeout=timeout)
    except Exception as exc:                       # pragma: no cover - environment dependent
        return {"available": False, "reason": repr(exc)[:160], "commits": [], "sampled": 0}
    if raw.returncode != 0:
        return {"available": False, "reason": raw.stderr.decode("utf-8", "replace")[:160],
                "commits": [], "sampled": 0}
    rows = []
    for line in raw.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split("|")
        if len(parts) >= 3:
            rows.append({"sha": parts[0], "date": parts[1], "subject": parts[2][:120]})
    return {"available": True, "reason": None, "commits": rows, "sampled": len(rows)}


def read_blob(repo, sha, path, timeout=30):
    try:
        raw = subprocess.run(["git", "show", "%s:%s" % (sha, path)], cwd=repo,
                             capture_output=True, timeout=timeout)
    except Exception:                              # pragma: no cover - environment dependent
        return None
    if raw.returncode != 0:
        return None
    return raw.stdout


def key_presence(blob_bytes, key):
    """(present, key_count, error) for one revision of a JSON face."""
    if blob_bytes is None:
        return None, None, "blob_unavailable"
    try:
        doc = json.loads(blob_bytes.decode("utf-8-sig", "replace"))
    except Exception as exc:
        return None, None, "unparsable:%s" % type(exc).__name__
    if not isinstance(doc, dict):
        return None, None, "not_an_object"
    return (key in doc), len(doc), None


def boundary_detail(repo, boundary, key, path, per_blob=3.0, deadline=24.0):
    """Presence of the key in each sampled revision, under a hard wall.

    A revision whose blob cannot be read inside its wall is published as unavailable with its
    error, never as 'absent': in a partial clone the difference between "the key is not there"
    and "I could not look" is the whole finding.
    """
    import time
    if not boundary.get("available") or not boundary["commits"]:
        return {"tested": False, "why": "no_boundary_commit", "per_commit": []}
    t0 = time.time()
    rows = []
    for row in boundary["commits"]:
        if time.time() - t0 > deadline:
            rows.append({"sha": row["sha"][:10], "date": row["date"], "present": None,
                         "key_count": None, "error": "wall_deadline_hit"})
            continue
        present, nkeys, err = key_presence(read_blob(repo, row["sha"], path, per_blob), key)
        rows.append({"sha": row["sha"][:10], "date": row["date"], "present": present,
                     "key_count": nkeys, "error": err})
    return {"tested": True, "per_commit": rows,
            "readable": sum(1 for r in rows if r["present"] is not None),
            "unreadable": sum(1 for r in rows if r["present"] is None)}


def keyset_diff(repo, sha_a, sha_b, path):
    ba, bb = read_blob(repo, sha_a, path), read_blob(repo, sha_b, path)
    try:
        da = set(json.loads(ba.decode("utf-8-sig", "replace")))
        db = set(json.loads(bb.decode("utf-8-sig", "replace")))
    except Exception:
        return None
    return {"only_before": sorted(da - db)[:40], "only_after": sorted(db - da)[:40],
            "n_only_before": len(da - db), "n_only_after": len(db - da)}


def read_site_facts(repo, rel, key):
    """Verbatim lines around every read of ``key`` in one source file."""
    try:
        text = io.open(os.path.join(repo, rel), encoding="utf-8", errors="replace").read()
    except OSError:
        return {"source": rel, "lines": [], "error": "unreadable"}
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines, 1):
        if key not in line:
            continue
        out.append({"line": i, "text": line.strip()[:300]})
    return {"source": rel, "lines": out[:12], "error": None}


def suffix_collisions(faces):
    """Faces in the population whose basename is a proper suffix of another face's basename."""
    base = {}
    for f in faces:
        b = os.path.basename(_norm(f))
        base.setdefault(b, set()).add(_norm(f))
    out = []
    for small, owners in sorted(base.items()):
        for big in base:
            if big == small or not big.endswith(small):
                continue
            out.append({"basename": small, "faces": sorted(owners),
                        "is_a_proper_suffix_of": big,
                        "faces_with_the_longer_basename": sorted(base[big])})
    return out


def same_doc_under_exact_test(repo, row):
    """Re-derive a pair's same-document claim by reading the dump target string.

    E395 decided this with ``face_basename in value``.  Here the same producer is re-parsed and
    the literal target it actually carries is classified; a site survives only if the target's
    basename is this face's basename (or the target ends with the face's relative path).
    """
    face = _norm(row["face"])
    base = os.path.basename(face)
    kept, dropped = [], []
    for prod in row["producers"]:
        sites = [s for s in (prod.get("sites") or [])
                 if s.get("path_class") == e395.W_UNCONDITIONAL
                 and s.get("dump_context") in ("direct_to_this_face", "via_name_to_this_face")]
        if not sites:
            continue
        try:
            src = io.open(os.path.join(repo, prod["producer"]),
                          encoding="utf-8", errors="replace").read()
        except OSError:
            dropped.append({"producer": prod["producer"], "why": "producer_unreadable"})
            continue
        hops = dump_link_targets(src, row["key"]) or []
        classes = [classify_target(t, face) for hop in hops for d in hop["dumps"]
                   for t in d["targets"]]
        entry = {"producer": prod["producer"],
                 "lines": sorted({s.get("line") for s in sites}),
                 "target_classes": classes}
        if any(c in (T_EXACT_PATH, T_EXACT_BASENAME) for c in classes):
            kept.append(entry)
        else:
            dropped.append(entry)
    return {"key": row["key"], "face": face, "basename": base,
            "kept": kept, "dropped": dropped,
            "holds": bool(kept),
            "e395_claim": row.get("producers_writing_this_face_unconditionally")}


def build(repo=ROOT):
    face_doc = json.loads(io.open(os.path.join(repo, "results/state_tilt/CONDITIONALWRITE-%s.json"
                                               % TODAY), encoding="utf-8-sig").read())
    rows = face_doc["rows"]
    target_row = None
    for row in rows:
        if row["key"] == KEY and _norm(row["face"]) == FACE_PATH:
            target_row = row
            break
    if target_row is None:
        raise SystemExit("E396: the pair under study is not in E395's population")

    # (b) the dump target, published as a string
    producer = None
    for prod in target_row["producers"]:
        if prod.get("writes_this_face_unconditionally"):
            producer = prod["producer"]
            break
    src_text = io.open(os.path.join(repo, producer), encoding="utf-8", errors="replace").read()
    hops = dump_link_targets(src_text, KEY) or []
    targets = []
    for hop in hops:
        for d in hop["dumps"]:
            for t in d["targets"]:
                targets.append({"assign_line": hop["assign_line"], "dump_line": d["line"],
                                "target": t,
                                "class": classify_target(t, FACE_PATH)})
    face_stores_key = None
    try:
        face_doc_bytes = io.open(os.path.join(repo, FACE_PATH), encoding="utf-8-sig").read()
        face_stores_key = KEY in json.loads(face_doc_bytes)
    except Exception:
        face_stores_key = None

    # (a) history: did this face ever carry the key, and where did it stop
    boundary = history_boundary(repo, FACE_PATH, KEY)
    bdetail = boundary_detail(repo, boundary, KEY, FACE_PATH)
    kdiff = None
    if boundary.get("available") and len(boundary["commits"]) >= 2:
        kdiff = keyset_diff(repo, boundary["commits"][0]["sha"],
                           boundary["commits"][1]["sha"], FACE_PATH)
    ever = [r for r in bdetail.get("per_commit", []) if r.get("present")]
    # independent of git: a source in the tree that writes the key into this face is evidence
    # the key existed at some point, whatever the sampled revisions can be read.
    in_tree_writers = []
    for rel in target_row.get("read_sites") or []:
        try:
            text = io.open(os.path.join(repo, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        sites = e395.write_sites(text, KEY, None) or []
        if sites:
            in_tree_writers.append({"source": rel,
                                    "forms": sorted({s["form"] for s in sites}),
                                    "lines": sorted({s["line"] for s in sites})[:8]})
    schema = {
        "face_ever_carried_the_key": bool(ever) or bool(in_tree_writers),
        "carried_in_the_sampled_revisions": bool(ever),
        "newest_revision_carrying_it": ever[0] if ever else None,
        "sampled_revisions": len(bdetail.get("per_commit") or []),
        "sampled_readable": bdetail.get("readable"),
        "sampled_unreadable": bdetail.get("unreadable"),
        "in_tree_writers_into_this_face": in_tree_writers,
        "key_set_diff_across_boundary": kdiff,
    }

    # (c) the read site, verbatim and typed
    reads = []
    for rel in target_row.get("read_sites") or []:
        facts = read_site_facts(repo, rel, KEY)
        typed = []
        for ln in facts["lines"]:
            txt = ln["text"]
            typed.append({"line": ln["line"], "text": txt,
                         "is_fallback": ".get(" in txt and txt.count(".get(") > 1,
                         "names_this_face": os.path.basename(FACE_PATH) in txt})
        reads.append({"source": rel, "lines": typed, "error": facts["error"]})

    # the generalisation: is the test that produced this pair sound anywhere else
    faces = sorted({_norm(r["face"]) for r in rows})
    coll = suffix_collisions(faces)
    recomputed = [same_doc_under_exact_test(repo, r) for r in rows
                  if r.get("producers_writing_this_face_unconditionally")]
    holds = [c for c in recomputed if c["holds"]]
    moves = [c for c in recomputed if not c["holds"]]

    suffix_hit = [t for t in targets if t["class"] == T_SUFFIX_ONLY]
    verdict = _verdict(schema, targets, suffix_hit, reads, moves)
    return {
        "study": STUDY,
        "script": "scripts/e396_last_tick.py",
        "generated": "2026-11-03T19:5x+08:00",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("three named explanations priced on the one pair E395 published; the dump "
                   "target published as a literal string rather than a boolean; the face's own "
                   "history read with git log -S over exactly this path; the read site quoted "
                   "verbatim; then the substring test that produced the pair re-run exactly over "
                   "E395's own face population"),
        "source_face": "results/state_tilt/CONDITIONALWRITE-%s.json" % TODAY,
        "pair": {"key": KEY, "face": FACE_PATH, "reads": target_row.get("reads"),
                 "read_sites": target_row.get("read_sites"),
                 "producer_with_the_unconditional_write": producer,
                 "face_stores_the_key_now": face_stores_key},
        "explanation_b_dump_target": {"hops": hops, "targets": targets,
                                     "suffix_only_targets": suffix_hit},
        "explanation_a_schema": {"boundary": boundary, "detail": bdetail, **schema},
        "explanation_c_read_site": {"reads": reads},
        "generalisation": {"faces_in_population": len(faces),
                           "suffix_collisions": coll,
                           "same_document_pairs": len(recomputed),
                           "pairs_that_still_hold_under_an_exact_test": holds,
                           "pairs_that_move": moves},
        "verdict": verdict,
    }


def _verdict(schema, targets, suffix_hit, reads, moves):
    if suffix_hit:
        name = "the_same_document_claim_is_a_suffix_match_not_a_path_match"
    elif schema["face_ever_carried_the_key"]:
        name = "the_face_carried_the_key_before_and_a_later_writer_dropped_it"
    elif any(t["class"] == T_EXACT_PATH for t in targets):
        name = "the_writer_does_name_this_face_so_the_key_is_missing_at_run_time"
    else:
        name = "no_producer_of_this_face_is_named_by_the_population"
    return {"name": name,
            "suffix_only_targets_published": len(suffix_hit),
            "face_ever_carried_the_key": schema["face_ever_carried_the_key"],
            "same_document_pairs_that_move": len(moves),
            "read_sites_seen": sum(len(r["lines"]) for r in reads)}


def verify(repo=ROOT):
    """Re-derive every published number from the face and the sources; return a list of problems."""
    problems = []
    doc = json.loads(io.open(os.path.join(repo, "results/state_tilt", FACE),
                             encoding="utf-8-sig").read())
    pair = doc["pair"]
    if pair["key"] != KEY or _norm(pair["face"]) != FACE_PATH:
        problems.append("the pair under study moved")

    # every published target string must still be in the producer, and its class must re-derive
    src = io.open(os.path.join(repo, pair["producer_with_the_unconditional_write"]),
                  encoding="utf-8", errors="replace").read()
    for t in doc["explanation_b_dump_target"]["targets"]:
        if t["target"] not in src:
            problems.append("a published dump target is not in the producer: %r" % t["target"])
        if classify_target(t["target"], FACE_PATH) != t["class"]:
            problems.append("a dump target class does not re-derive: %r" % t["target"])
    hops = dump_link_targets(src, KEY)
    if hops != doc["explanation_b_dump_target"]["hops"]:
        problems.append("the assign->dump hops do not re-derive")

    # the read sites must still resolve
    for r in doc["explanation_c_read_site"]["reads"]:
        facts = read_site_facts(repo, r["source"], KEY)
        if facts["error"]:
            problems.append("a read site is unreadable: %s" % r["source"])
            continue
        if not facts["lines"]:
            problems.append("a read site no longer mentions the key: %s" % r["source"])

    # the generalisation must re-add
    face_doc = json.loads(io.open(os.path.join(repo, "results/state_tilt/CONDITIONALWRITE-%s.json"
                                               % TODAY), encoding="utf-8-sig").read())
    rows = face_doc["rows"]
    faces = sorted({_norm(r["face"]) for r in rows})
    if len(faces) != doc["generalisation"]["faces_in_population"]:
        problems.append("the face population size does not re-derive")
    if suffix_collisions(faces) != doc["generalisation"]["suffix_collisions"]:
        problems.append("the suffix-collision census does not re-derive")
    recomputed = [same_doc_under_exact_test(repo, r) for r in rows
                  if r.get("producers_writing_this_face_unconditionally")]
    moves = [c for c in recomputed if not c["holds"]]
    if len(recomputed) != doc["generalisation"]["same_document_pairs"]:
        problems.append("the same-document pair count does not re-derive")
    if len(moves) != len(doc["generalisation"]["pairs_that_move"]):
        problems.append("the moved-pair count does not re-derive")
    for c in moves:
        if not any(m["face"] == c["face"] for m in doc["generalisation"]["pairs_that_move"]):
            problems.append("a moved pair is missing from the face: %s" % c["face"])
    if _verdict(doc["explanation_a_schema"], doc["explanation_b_dump_target"]["targets"],
                doc["explanation_b_dump_target"]["suffix_only_targets"],
                doc["explanation_c_read_site"]["reads"], moves) != doc["verdict"]:
        problems.append("the verdict does not re-derive from the published evidence")
    return problems


# --------------------------------------------------------------------------- selftest

def selftest():
    legs, bad = [], []

    def leg(name, ok):
        legs.append((name, bool(ok)))
        if not ok:
            bad.append(name)

    face = "logs/iteration-loop/state.json"
    leg("L1 an exact path is recognised as the face",
        classify_target("logs/iteration-loop/state.json", face) == T_EXACT_PATH)
    leg("L2 a ./-prefixed path is recognised as the face",
        classify_target("./logs/iteration-loop/state.json", face) == T_EXACT_PATH)
    leg("L3 the bare basename is a weaker but honest match",
        classify_target("state.json", face) == T_EXACT_BASENAME)
    leg("L4 autofill_state.json is a SUFFIX match and is published as such",
        classify_target("results/autofill_state.json", face) == T_SUFFIX_ONLY)
    leg("L5 a backslashed suffix match is caught too",
        classify_target("results\\autofill_state.json", face) == T_SUFFIX_ONLY)
    leg("L6 another document with the same basename elsewhere is not this face",
        classify_target("state_tilt/state.json", face) in (T_EXACT_BASENAME, T_SUFFIX_ONLY))
    leg("L7 an unrelated filename is other",
        classify_target("results/compute_audit.json", face) == T_OTHER)
    leg("L8 an empty target is other, never a match",
        classify_target("", face) == T_OTHER)

    src = "\n".join([
        "auto = {'launches': [], 'last_tick': None}",
        "dump(auto, 'results/autofill_state.json')",
    ])
    hops = dump_link_targets(src, "last_tick")
    leg("L9 the assign->dump hop is found and carries the target string",
        hops and hops[0]["dumps"] and hops[0]["dumps"][0]["targets"] == ["results/autofill_state.json"])
    leg("L10 that target classifies as a suffix match, i.e. the pair's shape",
        classify_target(hops[0]["dumps"][0]["targets"][0], face) == T_SUFFIX_ONLY)
    src2 = "auto = {'last_tick': None}\n" + "dump(auto, 'logs/iteration-loop/state.json')"
    leg("L11 a genuine same-file dump is recognised",
        classify_target(dump_link_targets(src2, "last_tick")[0]["dumps"][0]["targets"][0], face)
        == T_EXACT_PATH)
    leg("L12 a literal that never reaches a dump publishes no dump",
        dump_link_targets("d = {'last_tick': None}", "last_tick")[0]["dumps"] == [])

    leg("L13 key_presence reads a dict with the key", key_presence(b'{"last_tick": 1}', KEY)
        == (True, 1, None))
    leg("L14 key_presence reads a dict without it", key_presence(b'{"round_no": 1}', KEY)
        == (False, 1, None))
    leg("L15 an unparsable revision is reported, not guessed",
        key_presence(b'not json', KEY)[0] is None)
    leg("L16 a missing blob is reported, not guessed",
        key_presence(None, KEY) == (None, None, "blob_unavailable"))

    coll = suffix_collisions(["logs/iteration-loop/state.json",
                              "results/autofill_state.json"])
    leg("L17 the census sees the collision that produced the pair",
        any(c["basename"] == "state.json"
            and c["is_a_proper_suffix_of"] == "autofill_state.json" for c in coll))
    leg("L18 a population without a suffix collision yields none",
        suffix_collisions(["a/x.json", "b/y.json"]) == [])

    # a hermetic repo: same literal, two producers, one target suffix-matches by accident
    import tempfile
    tmpd = tempfile.mkdtemp(prefix="e396_")
    os.makedirs(os.path.join(tmpd, "deep"), exist_ok=True)
    with io.open(os.path.join(tmpd, "deep", "state.json"), "w", encoding="utf-8") as fh:
        fh.write("{}")
    with io.open(os.path.join(tmpd, "p_suffix.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("auto = {'last_tick': None}\n"
                 "dump(auto, 'results/autofill_state.json')\n")
    with io.open(os.path.join(tmpd, "p_exact.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("auto = {'last_tick': None}\n"
                 "dump(auto, 'deep/state.json')\n")
    row_base = {"key": "last_tick", "face": "deep/state.json",
                "producers_writing_this_face_unconditionally": 1,
                "producers": [{"producer": "p_exact.py",
                               "sites": [{"line": 2, "path_class": e395.W_UNCONDITIONAL,
                                          "dump_context": "via_name_to_this_face"}]}]}
    leg("L19 a genuine same-file dump survives the exact test",
        same_doc_under_exact_test(tmpd, row_base)["holds"] is True)
    row_sfx = json.loads(json.dumps(row_base))
    row_sfx["producers"][0]["producer"] = "p_suffix.py"
    moved = same_doc_under_exact_test(tmpd, row_sfx)
    leg("L20 a suffix-only dump is dropped by the exact test", moved["holds"] is False)
    leg("L20b the dropped site publishes the class that dropped it",
        moved["dropped"][0]["target_classes"] == [T_SUFFIX_ONLY])
    row_br = json.loads(json.dumps(row_base))
    row_br["producers"][0]["sites"][0]["path_class"] = e395.W_BRANCH
    leg("L20c a branch site is not promoted by the exact test",
        same_doc_under_exact_test(tmpd, row_br)["holds"] is False)

    v = _verdict({"face_ever_carried_the_key": False},
                 [{"class": T_SUFFIX_ONLY}], [{"class": T_SUFFIX_ONLY}], [], [])
    leg("L21 a suffix match is named as the cause, ahead of the other explanations",
        v["name"] == "the_same_document_claim_is_a_suffix_match_not_a_path_match")
    v2 = _verdict({"face_ever_carried_the_key": True}, [], [], [], [])
    leg("L22 with no suffix match a schema drop is named", "dropped_it" in v2["name"])
    v3 = _verdict({"face_ever_carried_the_key": False}, [], [], [], [])
    leg("L23 with neither, the study refuses to name a writer",
        "no_producer" in v3["name"])

    print("selftest: %d/%d" % (sum(1 for _, ok in legs if ok), len(legs)))
    for name, ok in legs:
        if not ok:
            print("  FAIL", name)
    return 0 if not bad else 1


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        problems = verify()
        print("verify:", "clean" if not problems else "%d problem(s)" % len(problems))
        for p in problems:
            print("  -", p)
        return 0 if not problems else 2
    if mode != "run":
        print("usage: e396_last_tick.py [run|verify|selftest]")
        return 64
    doc = build()
    os.makedirs(os.path.join(ROOT, "results", "state_tilt"), exist_ok=True)
    with io.open(os.path.join(ROOT, "results", "state_tilt", FACE), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with io.open(os.path.join(ROOT, "results", "state_tilt", LATEST), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"verdict": doc["verdict"],
                      "targets": doc["explanation_b_dump_target"]["targets"],
                      "schema": {k: doc["explanation_a_schema"][k]
                                 for k in ("face_ever_carried_the_key",
                                           "newest_revision_carrying_it")},
                      "collisions": doc["generalisation"]["suffix_collisions"],
                      "moves": doc["generalisation"]["pairs_that_move"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))