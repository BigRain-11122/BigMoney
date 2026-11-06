"""E471 -- is a never-opened pointer target a second copy of a face that is read, or content nobody reads?

E470 published 17 of 24 pointer targets that need a base other than the repo root and are never
opened by any site in the corpus.  A file nobody opens is one of two very different things:

  redundant   the same subject (or the very same bytes) is also published on a face that IS read,
              so the dead edge costs nothing -- the content is reachable, just through another door.
  orphaned    nothing else on disk carries it; the content exists in exactly one file that no
              program will ever open.

Two peer channels, published apart:

  EXACT_COPY     another file in the scoped directories has the same content hash.  JSON is
                 compared after a canonical re-serialisation and CRLF is folded to LF first, so a
                 checkout that changed line endings cannot pass for a copy (E461 family).
  SAME_SUBJECT   another file publishes the same subject: the same ``study`` value (falling back to
                 ``card`` then ``title``).  This is the vintage relation -- WIDTHLADDER-20261030 and
                 WIDTHLADDER-20261106 carry different numbers under one study.

The opened-status of every PEER is measured, never assumed: the peer set goes back through E470's
opener scan (``sites_for`` + ``residue_of``) with E468's writer map, so ``the peer is read`` means a
site turns its path into something the program can OPEN -- the same bar the parent applied to the
targets themselves.

Residues per never-opened target, most-reaching first:

  R_READ_PEER   a copy or same-subject sibling is opened by a study that writes neither face
  R_ONLY_LEG    the only effort that opens a peer is a smoke / runner leg or a one-off round script
  R_BLIND_PEER  peers exist but none of them is opened by anything either
  R_NO_PEER     there is no second copy on disk at all -- the content lives in one unread file

Scope limit that is published, not hidden: the copy census runs over the directories that publish
these subjects (the parents of the targets plus ``results/state_tilt``).  A copy living outside
those directories is not counted, so R_NO_PEER means "no copy where this subject is published",
not "no copy anywhere in the tree".

Run:      python scripts/e471_dead_copy.py run
Verify:   python scripts/e471_dead_copy.py verify   (re-derives from the live tree)
Check:    python scripts/e471_dead_copy.py check    (tallies re-derive from the face)
Selftest: python scripts/e471_dead_copy.py selftest
"""

import argparse
import ast  # noqa: F401  (kept for readers that expect the family's imports)
import datetime
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e468_pointer_reach as e468  # noqa: E402  (producer_map)
import e470_target_read as e470  # noqa: E402  (sites_for / residue_of / R_NEVER)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "deadcopy_latest.json"
DATED_PREFIX = "DEADCOPY"
CARD = "E471-IS-A-NEVER-OPENED-POINTER-TARGET-A-SECOND-COPY-OF-A-FACE-THAT-IS-READ-OR-CONTENT-NOBODY-READS"
SOURCE_FACE = os.path.join(OUTDIR, "targetread_latest.json")

SELF_SKIP = tuple(e470.SELF_SKIP) + ("e471_", "run_e471")
MAX_READ_BYTES = 2 * 1024 * 1024

# ---- peer channels -------------------------------------------------------------------------
C_EXACT = "the_same_content_after_a_canonical_re_serialisation"
C_SUBJECT = "the_same_subject_a_different_vintage"
CHANNELS = (C_EXACT, C_SUBJECT)

# ---- residues ------------------------------------------------------------------------------
R_READ_PEER = "a_peer_is_opened_by_a_study_that_writes_neither_face"
R_ONLY_LEG = "the_only_effort_that_opens_a_peer_is_a_smoke_leg_or_a_one_off_round_script"
R_BLIND_PEER = "peers_exist_but_none_of_them_is_opened_by_anything_either"
R_NO_PEER = "there_is_no_second_copy_where_this_subject_is_published"
RESIDUES = (R_READ_PEER, R_ONLY_LEG, R_BLIND_PEER, R_NO_PEER)

V_EMPTY = "the_parent_published_no_never_opened_target"
V_ALL_REDUNDANT = "every_never_opened_target_is_a_second_copy_of_a_face_that_is_read"
V_SOME_REDUNDANT = "some_never_opened_targets_are_second_copies_of_a_face_that_is_read_and_others_are_not"
V_NONE_REDUNDANT = "no_never_opened_target_has_a_peer_that_anything_opens"
VERDICT_VOCAB = (V_EMPTY, V_ALL_REDUNDANT, V_SOME_REDUNDANT, V_NONE_REDUNDANT)


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _now():
    return datetime.datetime.now().astimezone()


def _norm(text):
    return str(text).replace("\\", "/").strip()


def _rel(target, root):
    """Repo-relative spelling of a target, or '' when it points outside the tree."""
    t = _norm(target)
    r = _norm(root).rstrip("/")
    if os.path.isabs(t) or (len(t) > 1 and t[1] == ":"):
        if t.lower().startswith(r.lower() + "/"):
            return t[len(r) + 1:]
        return ""
    return t.lstrip("./")


def _canon_hash(path):
    """Content hash that survives a checkout: CRLF folded to LF, JSON re-serialised canonically."""
    with io.open(path, "rb") as fh:
        raw = fh.read()
    folded = raw.replace(b"\r\n", b"\n")
    if _norm(path).lower().endswith(".json"):
        try:
            obj = json.loads(folded.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            obj = None
        if obj is not None:
            canon = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            return "json-canonical:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()
    return "bytes-lf:" + hashlib.sha256(folded).hexdigest()


def _subject(path):
    """The subject a face declares, most-specific key first; '' when it declares none."""
    try:
        obj = _load(path)
    except (OSError, ValueError):
        return ""
    if not isinstance(obj, dict):
        return ""
    for key in ("study", "card", "title"):
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


# ------------------------------------------------------------------ population


def population(root=None):
    """The never-opened targets E470 published (residue R_NEVER), each with its pointing faces."""
    root = root or ROOT
    face = _load(os.path.join(root, "results", "state_tilt", "targetread_latest.json"))
    pop = []
    for row in face.get("rows") or []:
        if row.get("residue") != e470.R_NEVER:
            continue
        tgt = row.get("target")
        if not tgt:
            continue
        rel = _rel(tgt, root)
        if not rel:
            continue
        pop.append({
            "target": rel,
            "basename": os.path.basename(rel),
            "pointers": [{"face": p.get("face"), "key": p.get("key"), "value": p.get("value")}
                         for p in (row.get("pointers") or [])],
        })
    pop.sort(key=lambda r: r["target"])
    meta = {"source_face": "results/state_tilt/targetread_latest.json",
            "source_verdict": face.get("verdict"),
            "parent_never_opened": len(pop),
            "parent_distinct_targets": len(face.get("rows") or [])}
    return pop, meta


def scoped_dirs(pop, root):
    """The directories that publish these subjects: each target's parent plus state_tilt."""
    dirs = set()
    for rec in pop:
        parent = os.path.dirname(rec["target"])
        if parent:
            dirs.add(parent)
    dirs.add("results/state_tilt")
    return sorted(dirs)


def _dir_files(rel_dir, root):
    path = os.path.join(root, rel_dir)
    out = []
    if not os.path.isdir(path):
        return out
    for name in sorted(os.listdir(path)):
        p = os.path.join(path, name)
        if not os.path.isfile(p) or not name.lower().endswith(".json"):
            continue
        if any(name.startswith(s) for s in SELF_SKIP):
            continue
        try:
            if os.path.getsize(p) > MAX_READ_BYTES:
                continue
        except OSError:
            continue
        out.append(rel_dir + "/" + name)
    return out


def peers_for(pop, root=None):
    """{target: [{path, channels}]} -- every copy and every same-subject sibling."""
    root = root or ROOT
    dirs = scoped_dirs(pop, root)
    files = []
    for d in dirs:
        files.extend(_dir_files(d, root))
    hashes = {}
    subjects = {}
    for rel in files:
        try:
            hashes[rel] = _canon_hash(os.path.join(root, rel))
        except OSError:
            continue
        subj = _subject(os.path.join(root, rel))
        if subj:
            subjects.setdefault(subj, []).append(rel)
    out = {}
    for rec in pop:
        tgt = rec["target"]
        mine = hashes.get(tgt)
        subj = _subject(os.path.join(root, tgt)) if tgt in hashes else ""
        found = {}
        if mine:
            for rel, h in hashes.items():
                if rel != tgt and h == mine:
                    found.setdefault(rel, set()).add(C_EXACT)
        if subj:
            for rel in subjects.get(subj, []):
                if rel != tgt:
                    found.setdefault(rel, set()).add(C_SUBJECT)
        out[tgt] = [{"path": rel, "channels": sorted(found[rel])}
                    for rel in sorted(found)]
    return out, {"scoped_dirs": dirs, "files_in_scope": len(files),
                 "subjects_indexed": len(subjects)}


def peer_reads(peer_map, root=None):
    """Measure which peers a site actually opens -- the parent's own bar, not a re-derivation by eye."""
    root = root or ROOT
    flat = {}
    for peers in peer_map.values():
        for p in peers:
            flat.setdefault(p["path"], None)
    if not flat:
        return {}, {}
    pop = [{"target": rel, "basename": os.path.basename(rel)} for rel in sorted(flat)]
    sites, site_meta = e470.sites_for(pop, root)
    producers = e468.producer_map(root)
    verdicts = {}
    for rec in pop:
        verdicts[rec["target"]] = {
            "residue": e470.residue_of(sites.get(rec["target"]) or {}, producers),
            "openers": (sites.get(rec["target"]) or {}).get("openers") or [],
        }
    return verdicts, site_meta


def residue_of_target(peers, peer_verdicts):
    """Which residue a never-opened target falls into, given what its peers show."""
    if not peers:
        return R_NO_PEER
    opened = []
    for p in peers:
        v = peer_verdicts.get(p["path"]) or {}
        opened.append(v.get("residue"))
    if any(r == e470.R_OTHER for r in opened):
        return R_READ_PEER
    if any(r in (e470.R_PRODUCER, e470.R_SMOKE, e470.R_ROUND, e470.R_GLOB) for r in opened):
        return R_ONLY_LEG
    return R_BLIND_PEER


def verdict_for(summary):
    n = summary["never_opened_targets"]
    if n == 0:
        return V_EMPTY
    by = summary["residue_classes"]
    if by.get(R_READ_PEER) == n:
        return V_ALL_REDUNDANT
    if by.get(R_READ_PEER):
        return V_SOME_REDUNDANT
    return V_NONE_REDUNDANT


# ------------------------------------------------------------------ build


def build(write=True, root=None):
    root = root or ROOT
    pop, meta = population(root)
    peer_map, peer_meta = peers_for(pop, root)
    peer_verdicts, site_meta = peer_reads(peer_map, root)

    rows = []
    for rec in pop:
        tgt = rec["target"]
        peers = peer_map.get(tgt) or []
        residue = residue_of_target(peers, peer_verdicts)
        rows.append({
            "target": tgt,
            "basename": rec["basename"],
            "pointers": rec["pointers"],
            "pointing_faces": sorted({p["face"] for p in rec["pointers"] if p.get("face")}),
            "peers": [{"path": p["path"], "channels": p["channels"],
                       "peer_residue": (peer_verdicts.get(p["path"]) or {}).get("residue"),
                       "peer_openers": len((peer_verdicts.get(p["path"]) or {}).get("openers") or [])}
                      for p in peers],
            "peer_count": len(peers),
            "readable_peer_count": sum(1 for p in peers
                                       if (peer_verdicts.get(p["path"]) or {}).get("residue") == e470.R_OTHER),
            "residue": residue,
        })

    by_residue = {r: 0 for r in RESIDUES}
    for row in rows:
        by_residue[row["residue"]] += 1
    by_channel = {c: 0 for c in CHANNELS}
    for row in rows:
        seen = set()
        for p in row["peers"]:
            seen.update(p["channels"])
        for c in seen:
            by_channel[c] += 1
    summary = {
        "card": CARD,
        "never_opened_targets": len(rows),
        "parent_never_opened": meta["parent_never_opened"],
        "targets_on_disk": sum(1 for r in rows
                               if os.path.isfile(os.path.join(root, r["target"]))),
        "targets_with_a_peer": sum(1 for r in rows if r["peer_count"]),
        "targets_with_a_readable_peer": sum(1 for r in rows if r["readable_peer_count"]),
        "peer_edges_total": sum(r["peer_count"] for r in rows),
        "readable_peer_edges_total": sum(r["readable_peer_count"] for r in rows),
        "residue_classes": by_residue,
        "targets_by_channel": by_channel,
        "peers_measured": len(peer_verdicts),
        "peers_opened_by_a_study": sum(1 for v in peer_verdicts.values()
                                       if v.get("residue") == e470.R_OTHER),
    }
    face = {
        "card": CARD,
        "study": "E471_is_a_never_opened_pointer_target_a_second_copy_of_a_face_that_is_read",
        "title": "is a never-opened pointer target a second copy of a face that is read, or content nobody reads?",
        "evidence_cutoff": _now().strftime("%Y-%m-%d"),
        "population_source": meta,
        "peer_scope": peer_meta,
        "opener_scan": site_meta,
        "channels": list(CHANNELS),
        "residue_classes": list(RESIDUES),
        "summary": summary,
        "verdict_vocab": list(VERDICT_VOCAB),
        "verdict": verdict_for(summary),
        "rows": rows,
        "method_limits": [
            "the copy census is scoped to the directories that publish these subjects; a copy living "
            "elsewhere is not counted, so no_peer means no copy where the subject is published",
            "the subject key falls back study -> card -> title; a face that names its subject in prose "
            "is counted as having no subject rather than guessed",
            "peer opened-status reuses E470.sites_for, which keys on the lowercased basename; two peers "
            "that share a basename in different directories are indistinguishable to that scan",
            "an exact copy is a content claim, not a provenance claim: two files with the same canonical "
            "bytes may still differ in what wrote them last",
        ],
    }
    paths = None
    if write:
        stamp = _now().strftime("%Y-%m-%d")
        dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, stamp))
        latest = os.path.join(OUTDIR, FACE_NAME)
        blob = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for p in (dated, latest):
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(blob + "\n")
        paths = [os.path.relpath(dated, root).replace("\\", "/"),
                 os.path.relpath(latest, root).replace("\\", "/")]
    return face, paths


def _recompute_tallies(face):
    rows = face.get("rows") or []
    by_residue = {r: 0 for r in RESIDUES}
    for row in rows:
        if row.get("residue") in by_residue:
            by_residue[row["residue"]] += 1
    by_channel = {c: 0 for c in CHANNELS}
    for row in rows:
        seen = set()
        for p in row.get("peers") or []:
            seen.update(p.get("channels") or [])
        for c in seen:
            by_channel[c] += 1
    return {
        "never_opened_targets": len(rows),
        "targets_with_a_peer": sum(1 for r in rows if r.get("peer_count")),
        "targets_with_a_readable_peer": sum(1 for r in rows if r.get("readable_peer_count")),
        "peer_edges_total": sum(r.get("peer_count") or 0 for r in rows),
        "readable_peer_edges_total": sum(r.get("readable_peer_count") or 0 for r in rows),
        "residue_classes": by_residue,
        "targets_by_channel": by_channel,
    }


def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    for row in rows:
        if row.get("residue") not in RESIDUES:
            problems.append("row %s carries an unknown residue %r" % (row.get("target"), row.get("residue")))
        readable = sum(1 for p in (row.get("peers") or [])
                       if p.get("peer_residue") == e470.R_OTHER)
        if readable != row.get("readable_peer_count"):
            problems.append("row %s readable count %r != peers showing a reading study %d"
                            % (row.get("target"), row.get("readable_peer_count"), readable))
        if len(row.get("peers") or []) != row.get("peer_count"):
            problems.append("row %s peer count %r != peers listed %d"
                            % (row.get("target"), row.get("peer_count"), len(row.get("peers") or [])))
        want = R_READ_PEER if readable else None
        if want and row.get("residue") != want:
            problems.append("row %s has a readable peer but residue %r"
                            % (row.get("target"), row.get("residue")))
        if not row.get("pointers"):
            problems.append("row %s names no pointing face" % row.get("target"))
    summary = face.get("summary") or {}
    derived = _recompute_tallies(face)
    for key, val in derived.items():
        if summary.get(key) != val:
            problems.append("summary %s %r != re-derived %r" % (key, summary.get(key), val))
    if face.get("verdict") != verdict_for({"never_opened_targets": derived["never_opened_targets"],
                                           "residue_classes": derived["residue_classes"]}):
        problems.append("verdict does not re-derive from the tallies")
    return problems


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = row_problems(face)
    print(json.dumps({"face": FACE_NAME, "problems": problems, "verdict": face.get("verdict")},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify():
    """Re-derive on the live tree and compare against the published face, shape for shape."""
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    live, _ = build(write=False)
    problems = []
    if published.get("verdict") != live.get("verdict"):
        problems.append("verdict %r != live %r" % (published.get("verdict"), live.get("verdict")))
    pv = (published.get("summary") or {}).get("residue_classes") or {}
    lv = live["summary"]["residue_classes"]
    if pv != lv:
        problems.append("residue classes %r != live %r" % (pv, lv))
    pr = {r["target"]: r["residue"] for r in published.get("rows") or []}
    lr = {r["target"]: r["residue"] for r in live["rows"]}
    if pr != lr:
        diff = [t for t in sorted(set(pr) | set(lr)) if pr.get(t) != lr.get(t)]
        problems.append("rows differ on %d target(s): %s" % (len(diff), diff[:6]))
    print(json.dumps({"verify": "identical" if not problems else "differs",
                      "problems": problems, "live_summary": live["summary"]},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1))


def _fixture(tmp):
    """Three never-opened targets: a redundant one, a blind-copy one and a lone one.

    The reader is a plain script that opens the redundant target's sibling by its whole
    repo-relative path, so the parent's opener scan has a real site to find.
    """
    st = os.path.join(tmp, "results", "state_tilt")
    os.makedirs(st, exist_ok=True)
    # redundant: same subject, one vintage opened, one vintage pointed at and never opened
    _write(os.path.join(st, "SUBJ-20261001.json"), {"study": "E999_fixture_subject", "v": 1})
    _write(os.path.join(st, "SUBJ-20261002.json"), {"study": "E999_fixture_subject", "v": 2})
    _write(os.path.join(st, "SUBJ_latest.json"), {"study": "E999_fixture_subject", "v": 2})
    # blind copy: two files with identical content, neither opened
    _write(os.path.join(st, "BLINDA.json"), {"study": "E998_blind", "v": 1})
    _write(os.path.join(st, "BLINDB.json"), {"study": "E998_blind", "v": 1})
    # lone: nothing else carries this subject
    _write(os.path.join(st, "ALONE.json"), {"study": "E997_alone", "v": 1})
    # the only reader in the fixture: opens SUBJ_latest by full path
    _write(os.path.join(tmp, "scripts", "reader_fixture.py"),
           {"ignored": True})
    with io.open(os.path.join(tmp, "scripts", "reader_fixture.py"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write("import json\n\n\ndef load():\n"
                 "    with open('results/state_tilt/SUBJ_latest.json', encoding='utf-8') as fh:\n"
                 "        return json.load(fh)\n")
    rows = []
    for tgt, face in (("results/state_tilt/SUBJ-20261002.json", "results/state_tilt/SUBJPOINT.json"),
                      ("results/state_tilt/BLINDB.json", "results/state_tilt/BLINDPOINT.json"),
                      ("results/state_tilt/ALONE.json", "results/state_tilt/ALONEPOINT.json")):
        rows.append({"target": tgt, "residue": e470.R_NEVER,
                     "pointers": [{"face": face, "key": "face", "value": tgt}]})
        _write(os.path.join(tmp, face), {"face": tgt})
    _write(os.path.join(st, "targetread_latest.json"),
           {"verdict": "some_targets_that_need_another_base_are_never_opened_by_any_site",
            "rows": rows})
    return tmp


def selftest():
    import tempfile
    import shutil
    legs = []

    tmp = tempfile.mkdtemp(prefix="e471_")
    try:
        _fixture(tmp)
        pop, meta = population(tmp)
        legs.append(("population reads the parent face", len(pop) == 3))
        legs.append(("population keeps only the never-opened residue", meta["parent_distinct_targets"] == 3))
        face, _ = build(write=False, root=tmp)
        by = {r["target"].rsplit("/", 1)[-1]: r for r in face["rows"]}
        legs.append(("a same-subject sibling that is opened makes the dead edge redundant",
                     by["SUBJ-20261002.json"]["residue"] == R_READ_PEER))
        legs.append(("the readable peer is named with its channel",
                     by["SUBJ-20261002.json"]["peers"]
                     and any(p["path"].endswith("SUBJ_latest.json")
                             and C_SUBJECT in p["channels"] for p in by["SUBJ-20261002.json"]["peers"])))
        legs.append(("an unopened exact copy is a blind peer, not a redundancy",
                     by["BLINDB.json"]["residue"] == R_BLIND_PEER))
        legs.append(("an exact copy is reported on the exact channel",
                     any(C_EXACT in p["channels"] for p in by["BLINDB.json"]["peers"])))
        legs.append(("a target with no second copy is a no-peer residue",
                     by["ALONE.json"]["residue"] == R_NO_PEER))
        legs.append(("verdict says some targets are redundant, not all",
                     face["verdict"] == V_SOME_REDUNDANT))
        legs.append(("summary counts one readable target",
                     face["summary"]["targets_with_a_readable_peer"] == 1))
        problems = row_problems(face)
        legs.append(("the published face is internally consistent", problems == []))

        # a doctored tally must be caught
        doctored = json.loads(json.dumps(face))
        doctored["summary"]["targets_with_a_readable_peer"] = 2
        legs.append(("a doctored tally fails the row guard", row_problems(doctored) != []))

        # a CRLF checkout of the same JSON must hash the same as the LF original
        path = os.path.join(tmp, "results", "state_tilt", "SUBJ-20261001.json")
        with io.open(path, "rb") as fh:
            body = fh.read()
        twin = os.path.join(tmp, "results", "state_tilt", "SUBJ_crlf_twin.json")
        with io.open(twin, "wb") as fh:
            fh.write(body.replace(b"\n", b"\r\n"))
        legs.append(("CRLF folding keeps a copy a copy", _canon_hash(path) == _canon_hash(twin)))
        # key order and whitespace are not content
        h1 = _canon_hash(path)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write('{\n   "v": 1,\n   "study": "E999_fixture_subject"\n}\n')
        legs.append(("canonical hashing ignores key order and whitespace", _canon_hash(path) == h1))
        # ...but a changed value is a different copy
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write('{"v": 2, "study": "E999_fixture_subject"}\n')
        legs.append(("a changed value is not a copy", _canon_hash(path) != h1))

        # the residue vocabulary stays closed
        legs.append(("every residue is reachable from the vocabulary",
                     set(RESIDUES) == {R_READ_PEER, R_ONLY_LEG, R_BLIND_PEER, R_NO_PEER}))
        legs.append(("a face with no rows yields the empty verdict",
                     verdict_for({"never_opened_targets": 0, "residue_classes": {}}) == V_EMPTY))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


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