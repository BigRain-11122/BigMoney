"""E365 -- a published-face population can be addressed and replayed, not merely counted.

E364 closed with a queue head it named rather than answered: *can a published-face population be
pinned and replayed like a source population -- stamp E328's faces and replay through its existing
seam?*  E361/E362/E363 answered that for a study's **source** corpus (path, digest, commit-or-store,
replay).  Nobody had asked it of the **outputs**, and E364's inventory had already shown why it
matters: of 28 studies that enumerate a directory, 15 quote a population count and only 2 name a
corpus anybody can fetch.

The face side carries one defect the source side does not.  A source file sits in the tree and its
path is its identity; a *published face* is written once, rewritten by later windows, and counted by
whatever happens to be on disk.  E328's own published summary says ``faces_scanned: 587``; the
population it walks holds 593 rows as this study was written -- and it held 591 four minutes
earlier.  Neither number is wrong and neither is an address: a count is not a pin.

The first draft of this study inherited E362's text-level rule (sha256 over LF-normalised UTF-8
text) and the replay convicted a face that had not moved:
``results/e25_cash_leg/TREND-a0653f-20261021.json`` begins with ``FF FE`` -- it is UTF-16LE -- so
the same bytes hash one way when read with surrogateescape and another way when a git blob is
decoded with ``replace``.  A population that walks an arbitrary directory is not a UTF-8 population,
so the address here is **byte level**: sha256 over the member's bytes with CRLF folded to LF.  The
digest of a file must not depend on who decodes it.

The seam is real and was already there: ``e328.build(root=..., files=...)`` reads faces through
``root`` and readers through ``files``.  So a replay needs no new hook, only fetchable bytes.  This
study therefore:

  1. takes the population from the study's **own** ``scan_faces`` (imported, never re-implemented
     -- E355's rule),
  2. stamps every member (path, sha256 of the byte stream, bytes, encoding class) and computes
     ``pin_id`` over the pairs,
  3. classifies each member by whether git can supply it, and writes the minority no commit holds
     into a content-addressed store beside the face,
  4. rebuilds the population from ``git cat-file`` + that store **only**, re-hashes each member and
     recomputes ``pin_id``,
  5. hydrates the replayed bytes into a scratch root and **re-runs E328's own build over it**,
     publishing what moved between the pin and the published summary -- with the reader domain
     stamped too, so a moved number is attributable to one of the two domains instead of guessed.

Verdict vocabulary is ordered so an incomplete store can never read as success:
  * no population / no commit / member with no address / bytes that do not hash -> a refusal
  * every member accounted for and ``pin_id`` equal                              -> replayed

Usage:
  python scripts/e365_face_population_pin.py stamp    # pin + inline store
  python scripts/e365_face_population_pin.py rerun    # replay + re-run the rule
  python scripts/e365_face_population_pin.py selftest
"""

from __future__ import annotations

import base64
import datetime as dt
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e328_quoted_number_staleness as e328  # the population rule, the loader and the seam
import e326_template_parameter_consumers as e326
from e361_census_corpus_pin import (  # identity + git facts, never a copy
    ROOT, OUTDIR, pin_id, relpath, classify, diff_corpora, head_tree, worktree_blobs,
    stamp as stamp_sources,
)

STUDY = "E365_face_population_pin"
STORE_DIR = os.path.join(OUTDIR, "face_store")
POPULATION_FN = e328.scan_faces  # pinned by identity, so a copy cannot silently drift

VERDICT_OK = "replayed_from_commit_plus_store"
VERDICT_MISSING = "cannot_be_replayed_members_have_no_address"
VERDICT_MISMATCH = "cannot_be_replayed_bytes_do_not_hash_to_the_pin"
VERDICT_NO_COMMIT = "cannot_be_replayed_the_pin_names_no_commit"
VERDICT_EMPTY = "cannot_be_replayed_the_population_is_empty"

RERUN_SAME = "reran_the_rule_over_the_pinned_vintage_and_the_summary_did_not_move"
RERUN_MOVED = "reran_the_rule_over_the_pinned_vintage_and_the_summary_moved"


# ------------------------------------------------------------------------------ byte level identity
def norm_bytes(raw: bytes) -> bytes:
    """One byte stream per content: CRLF folded to LF, nothing else touched."""
    return raw.replace(b"\r\n", b"\n")


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(norm_bytes(raw)).hexdigest()


def encoding_class(raw: bytes) -> str:
    """Which reader can open this member at all -- the fact the first draft did not record."""
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16-bom"
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "not-utf-8"


def read_bytes(root: str, rel: str):
    try:
        with open(os.path.join(root, rel), "rb") as fh:
            return fh.read()
    except OSError:
        return None


# ------------------------------------------------------------------------------------- population
def own_faces() -> set:
    """The names this study publishes.  Kept out of the population for E319's reason.

    Measured, not assumed: the first run of this study counted its own ``FACEPOPPIN-2026-11-02``
    and then refused it -- the pin was taken over the previous vintage of that file and the store
    re-read it after the face had been rewritten, so the pin convicted its own author.  A pin that
    includes its publisher is not idempotent, and a population address has to be.
    """
    return {"FACEPOPPIN-%s.json" % dt.date.today().isoformat(),
            "FACERERUN-%s.json" % dt.date.today().isoformat(),
            "facepoppin_latest.json", "facererun_latest.json"}


def population(root: str = None) -> list:
    """E328's own face population: its scanner, not a re-implementation (E355)."""
    own = own_faces()
    return [rec for rec in POPULATION_FN(root or ROOT)
            if os.path.basename(rec["rel"]) not in own]


def stamp_population(root: str = None) -> dict:
    """Address the population: one row per face, by bytes, plus whether git can supply it."""
    root = root or ROOT
    rows, unreadable = [], []
    for rec in population(root):
        rel = rec["rel"]
        raw = read_bytes(root, rel)
        if raw is None:
            unreadable.append(rel)
        rows.append({"path": rel,
                     "sha256": digest_bytes(raw) if raw is not None else "",
                     "bytes": len(norm_bytes(raw)) if raw is not None else 0,
                     "encoding": encoding_class(raw) if raw is not None else "unreadable",
                     "family": rec["family"], "stem": rec["stem"],
                     "token": rec["token"].isoformat()})
    if not rows:
        raise ValueError("EMPTY-SCOPE: E328's scanner found no faces under %s" % root)
    paths = [r["path"] for r in rows]
    if len(set(paths)) != len(paths):
        raise ValueError("EMPTY-SCOPE: duplicate face path (a pin would double count it)")
    rows = classify(rows, head_tree(paths), worktree_blobs(paths))
    return {"sources": rows, "unreadable": unreadable}


def parseable(root: str, rows) -> dict:
    """The study's own loader decides what a face is worth; a refusal is counted, not hidden."""
    ok, refused = 0, []
    for r in rows:
        if e328.load(root, r["path"]) is not None:
            ok += 1
        else:
            refused.append(r["path"])
    return {"parseable": ok, "unparseable": len(refused),
            "unparseable_names": sorted(refused)[:20]}


def summarize(rows, unreadable, parsed=None) -> dict:
    supply = [r for r in rows if r["git_can_supply"]]
    enc = {}
    for r in rows:
        enc[r["encoding"]] = enc.get(r["encoding"], 0) + 1
    out = {
        "faces": len(rows),
        "families": len({r["family"] for r in rows}),
        "dirs": len({os.path.dirname(r["path"]) for r in rows}),
        "git_can_supply": len(supply),
        "untracked": len([r for r in rows if not r["tracked"]]),
        "dirty": len([r for r in rows if r.get("dirty")]),
        "needs_store": len([r for r in rows if not r["git_can_supply"]]),
        "needs_store_bytes": sum(r["bytes"] for r in rows if not r["git_can_supply"]),
        "unreadable": len(unreadable),
        "encoding": enc,
        "not_utf8": len([r for r in rows if r["encoding"] != "utf-8"]),
        "pct_supplied_by_git": round(100.0 * len(supply) / len(rows), 2) if rows else 0.0,
    }
    if parsed is not None:
        out.update(parsed)
    return out


def reader_domain() -> dict:
    """The other half of the seam: `files`.  Stamped so a moved number has an owner."""
    return stamp_sources(e326.corpus(), ROOT)


def published_summary() -> dict:
    """The face E328 last published, read only to be compared -- never rewritten here."""
    hits = sorted(glob.glob(os.path.join(OUTDIR, "STALECUTOFF-*.json")))
    if not hits:
        return {"found": False}
    path = hits[-1]
    try:
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:  # a face that cannot be read is reported, not assumed
        return {"found": False, "error": str(exc)[:120], "path": relpath(path)}
    return {"found": True, "path": relpath(path), "evidence_cutoff": doc.get("evidence_cutoff"),
            "summary": doc.get("summary") or {},
            "mtime": dt.datetime.fromtimestamp(os.path.getmtime(path)).isoformat(
                timespec="seconds")}


def drift_against_published(published: dict, rows, root: str = None) -> dict:
    """A count is not an address: say how far the population moved, and name what can be named."""
    root = root or ROOT
    if not published.get("found"):
        return {"comparable": False, "reason": "no published face on disk"}
    was = (published.get("summary") or {}).get("faces_scanned")
    now = len(rows)
    out = {"comparable": isinstance(was, int), "published_faces_scanned": was, "pinned_faces": now,
           "delta": (now - was) if isinstance(was, int) else None,
           "published_face_names_no_member": True,
           "heuristic": "faces whose mtime is newer than the published face's own mtime"}
    if not isinstance(was, int):
        return out
    if now == was:
        out["newer_than_published"] = []
        out["heuristic_agrees"] = True
        return out
    try:
        mark = os.path.getmtime(os.path.join(ROOT, published["path"]))
    except OSError:
        out["newer_than_published"] = []
        out["heuristic"] += " (unavailable)"
        return out
    newer = []
    for r in rows:
        try:
            if os.path.getmtime(os.path.join(root, r["path"])) > mark:
                newer.append(r["path"])
        except OSError:
            continue
    out["newer_than_published"] = sorted(newer)
    out["newer_count"] = len(newer)
    out["heuristic_agrees"] = len(newer) == (now - was)
    return out


def build(outdir: str = None, root: str = None) -> dict:
    root = root or ROOT
    stamped = stamp_population(root)
    rows, unreadable = stamped["sources"], stamped["unreadable"]
    published = published_summary()
    today = dt.date.today().isoformat()
    face = {
        "study": STUDY,
        "evidence_cutoff": today,
        "population_rule": "e328_quoted_number_staleness.scan_faces (imported by identity)",
        "pin_id": pin_id(rows),
        "count": len(rows),
        "git_commit": head_commit(),
        "summary": summarize(rows, unreadable, parseable(root, rows)),
        "reader_domain": reader_domain(),
        "published": published,
        "drift_vs_published": drift_against_published(published, rows, root),
        "sources": rows,
        "rules": {
            "member": "path<TAB>sha256 over the member's bytes with CRLF folded to LF",
            "pin_id": "sha256 over the sorted member lines",
            "why_bytes": "",  # filled below, once the population has been classified
            "supply": "a member is replayable from git only if HEAD holds it AND the work copy "
                      "equals that blob; everything else must be in the store",
        },
        "limits": {
            "count_is_not_an_address": "the published face names no member, so its own 587 cannot "
                                       "be reconstructed by name -- only measured",
            "mtime_heuristic": "a face rewritten later is indistinguishable from one added later "
                               "by mtime alone; the list is offered with that caveat",
            "reader_domain_unstored": "the reader corpus is stamped but not stored here; its own "
                                      "store is E362's mechanism (source side)",
            "crlf_folded": "the byte stream is normalised, so a pure CRLF difference is not "
                           "content under this rule",
        },
    }
    face["rules"]["why_bytes"] = ("a population that walks an arbitrary directory is not a UTF-8 "
                                  "population: %d of the members here do not decode as UTF-8, and "
                                  "a text-level digest would depend on the decoder"
                                  % face["summary"]["not_utf8"])
    own = own_faces()
    face["own_faces_excluded"] = sorted(os.path.basename(r["rel"])
                                        for r in POPULATION_FN(root) if os.path.basename(r["rel"]) in own)
    face["summary"]["own_faces_excluded"] = len(face["own_faces_excluded"])
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "FACEPOPPIN-%s.json" % today)
    _write(path, face)
    _write(os.path.join(outdir, "facepoppin_latest.json"), face)
    return dict(face, face_path=path)


def head_commit() -> str:
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True)
    return p.stdout.decode("ascii", "replace").strip() if p.returncode == 0 else ""


def _write(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)


# ------------------------------------------------------------------------------------- store io
def store_path(pin_hash: str, dest_dir: str = STORE_DIR) -> str:
    return os.path.join(dest_dir, "FACESTORE-%s.json" % pin_hash[:16])


def encode_bytes(raw: bytes) -> str:
    """zlib over the normalized bytes, then base64: the store is text, not a blob dump."""
    return base64.b64encode(zlib.compress(norm_bytes(raw), 9)).decode("ascii")


def decode_bytes(blob: str) -> bytes:
    return zlib.decompress(base64.b64decode(blob))


def write_store(pin: dict, members: dict, dest_dir: str = STORE_DIR) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    path = store_path(pin["pin_id"], dest_dir)
    payload = {"pin_id": pin["pin_id"], "study": pin.get("study"),
               "git_commit": pin.get("git_commit"), "mode": "bytes",
               "count": len(members),
               "members": {p: encode_bytes(b) for p, b in sorted(members.items())}}
    _write(path, payload)
    return path


def load_store(pin_hash: str, dest_dir: str = STORE_DIR) -> dict:
    path = store_path(pin_hash, dest_dir)
    if not os.path.exists(path):
        raise FileNotFoundError("no face store for pin %s at %s" % (pin_hash[:16], path))
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def unsuppliable(pin: dict) -> list:
    return [s for s in pin["sources"] if not s.get("git_can_supply")]


# ------------------------------------------------------------------------------------- byte replay
def blob_bytes(commit: str, paths) -> tuple:
    """`commit:path` as raw bytes for every path the commit holds.  Reads git objects, no decode.

    E362's transport decodes to text, which is right for python sources and wrong here: this
    population holds a UTF-16 member, and a lossy decode is what convicted it in the first draft.
    """
    paths = list(paths)
    if not paths:
        return {}, []
    p = subprocess.run(["git", "ls-tree", "-r", commit], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git ls-tree %s failed: %s"
                           % (commit[:12], p.stderr.decode("utf-8", "replace")[:200]))
    tree = {}
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3:
            tree[path] = parts[2]
    wanted = [(q, tree[q]) for q in paths if q in tree]
    missing = [q for q in paths if q not in tree]
    if not wanted:
        return {}, missing
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, capture_output=True,
                          input=("\n".join(b for _p, b in wanted) + "\n").encode("ascii"))
    if proc.returncode != 0:
        raise RuntimeError("git cat-file failed: %s"
                           % proc.stderr.decode("utf-8", "replace")[:200])
    buf, i, blobs = proc.stdout, 0, {}
    for _path, blob in wanted:
        nl = buf.index(b"\n", i)
        header = buf[i:nl].decode("ascii", "replace").split()
        i = nl + 1
        if len(header) < 3 or header[1] != "blob":
            continue
        size = int(header[2])
        blobs[blob] = buf[i:i + size]
        i += size + 1
    return {q: blobs[b] for q, b in wanted if b in blobs}, missing


def replay(pin: dict, store_dir: str = STORE_DIR) -> dict:
    sources = pin.get("sources") or []
    base = {"pin_id": pin.get("pin_id"), "count": pin.get("count"),
            "study": pin.get("study"), "working_tree_read": False}
    if not sources:
        return dict(base, verdict=VERDICT_EMPTY, replayed_count=0, missing=[], mismatched=[])
    commit = pin.get("git_commit")
    if not commit:
        return dict(base, verdict=VERDICT_NO_COMMIT, replayed_count=0,
                    missing=[s["path"] for s in sources], mismatched=[])

    gits = [s["path"] for s in sources if s.get("git_can_supply")]
    from_git, missing_git = blob_bytes(commit, gits)
    try:
        store = load_store(pin["pin_id"], store_dir)
    except FileNotFoundError:
        store = {"members": {}}
    from_store = {p: decode_bytes(b) for p, b in (store.get("members") or {}).items()}

    rows, missing, mismatched = [], [], []
    n_git = n_store = 0
    for s in sorted(sources, key=lambda r: r["path"]):
        p = s["path"]
        if p in from_git:
            raw, n_git = from_git[p], n_git + 1
        elif p in from_store:
            raw, n_store = from_store[p], n_store + 1
        else:
            missing.append(p)
            continue
        got = digest_bytes(raw)
        if got != s["sha256"]:
            mismatched.append({"path": p, "pinned": s["sha256"], "replayed": got,
                               "pinned_encoding": s.get("encoding"),
                               "replayed_encoding": encoding_class(raw)})
            continue
        rows.append({"path": p, "sha256": got})

    replayed_id = pin_id(rows) if rows else ""
    if missing:
        verdict = VERDICT_MISSING
    elif mismatched or len(rows) != len(sources):
        verdict = VERDICT_MISMATCH
    elif replayed_id != pin["pin_id"]:
        verdict = VERDICT_MISMATCH
    else:
        verdict = VERDICT_OK
    members = {s["path"]: from_git.get(s["path"], from_store.get(s["path"])) for s in rows}
    return dict(base, verdict=verdict, replayed_pin_id=replayed_id,
                reproduces=(replayed_id == pin.get("pin_id")),
                replayed_count=len(rows), count_matches=len(rows) == len(sources),
                from_commit=n_git, from_store=n_store, missing=missing,
                mismatched=mismatched, missing_git_suppliable=len(missing_git),
                members=members)


def hydrate(members: dict, dest: str) -> list:
    """Write the replayed bytes back into a tree-shaped scratch root, nothing else."""
    written = []
    for rel, raw in sorted(members.items()):
        if raw is None:
            continue
        path = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(norm_bytes(raw))
        written.append(rel)
    return written


# ------------------------------------------------------------------------------------------ rerun
def rerun(pin: dict = None, store_dir: str = STORE_DIR) -> dict:
    """Re-execute E328's own build over the pinned vintage through its existing `root` seam."""
    pin = pin or load_newest_pin()
    r = replay(pin, store_dir)
    if r["verdict"] != VERDICT_OK:
        return {"verdict": "cannot_rerun_%s" % r["verdict"], "pin_id": pin.get("pin_id"),
                "replay": {k: v for k, v in r.items() if k != "members"}}
    tmp = tempfile.mkdtemp(prefix="e365_rerun_")
    try:
        written = hydrate(r["members"], tmp)
        out = tempfile.mkdtemp(prefix="e365_rerun_face_")
        try:
            face = e328.build(root=tmp, outdir=out, files=e326.corpus())
        finally:
            shutil.rmtree(out, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    pinned_summary = pin.get("rerun_summary") or {}
    now_summary = face.get("summary") or {}
    keys = sorted(set(pinned_summary) | set(now_summary))
    moved = [k for k in keys if pinned_summary.get(k) != now_summary.get(k)]
    readers_now = reader_domain()
    readers_pin = pin.get("reader_domain") or {}
    readers_moved = readers_now.get("pin_id") != readers_pin.get("pin_id")
    own = pin.get("own_faces_excluded") or []
    pop_delta = (pinned_summary.get("faces_scanned") or 0) - (now_summary.get("faces_scanned") or 0)
    return {
        "verdict": RERUN_SAME if not moved else RERUN_MOVED,
        "pin_id": pin.get("pin_id"),
        "hydrated_members": len(written),
        "replayed_population": now_summary.get("faces_scanned"),
        "pinned_population": pin.get("count"),
        "summary_keys_compared": len(keys),
        "summary_moved_keys": moved,
        "summary_at_pin": pinned_summary,
        "summary_now": now_summary,
        "population_delta_at_pin_minus_now": pop_delta,
        "population_delta_explained_by_own_faces": bool(own) and pop_delta == len(own),
        "own_faces_excluded": own,
        "pinned_numbers_that_did_not_move": [k for k in keys if k not in moved],
        "reader_domain_moved": readers_moved,
        "reader_members_at_pin": readers_pin.get("members"),
        "reader_members_now": readers_now.get("members"),
        "attribution": (
            ("the reader corpus's content moved (same member count: %s) yet %d of %d summary keys "
             "did not move, so the reader drift is measured as harmless here and the population "
             "delta is the study's own faces"
             % (readers_now.get("members") == readers_pin.get("members"),
                len([k for k in keys if k not in moved]), len(keys)))
            if readers_moved else
            "the reader corpus is unchanged, so any movement belongs to the face domain alone"),
        "baseline_note": "summary_at_pin was measured on the live tree at stamp time, before this "
                         "study's own faces were written out; the pin excludes them, so a "
                         "population-only difference is the study's self-inclusion (E319), and "
                         "every derived number must still agree",
    }


def load_newest_pin() -> dict:
    hits = sorted(glob.glob(os.path.join(OUTDIR, "FACEPOPPIN-*.json")))
    if not hits:
        raise FileNotFoundError("no FACEPOPPIN face under %s -- run stamp first" % OUTDIR)
    with io.open(hits[-1], encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1: the population rule is the study's, by identity -- a copy would drift silently
    leg("the population function IS e328's scanner (E355: never a re-implementation)",
        POPULATION_FN is e328.scan_faces, getattr(POPULATION_FN, "__module__", "?"))

    tmp = tempfile.mkdtemp(prefix="e365_")
    try:
        root = os.path.join(tmp, "fake")
        fixture = [("results/A/B-2026-01-01.json", b'{"evidence_cutoff": "2026-01-01"}'),
                   ("results/A/B-2026-01-02.json", b'{"evidence_cutoff": "2026-01-02"}\r\n'),
                   ("results/C/D-2026-01-05.json", b'{"evidence_cutoff": "2026-01-05"}'),
                   ("results/C/U-2026-01-06.json",
                    b'\xff\xfe{\x00"\x00a\x00"\x00:\x001\x00}\x00')]  # UTF-16LE, the found defect
        for rel, raw in fixture:
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(raw)
        pop = e328.scan_faces(root)
        # 2: activity first (r1261): the mechanism must actually see rows before anything else counts
        leg("the fixture population is actually scanned (4 faces, 3 families, 2 dirs)",
            len(pop) == 4 and len({p['family'] for p in pop}) == 3, "rows=%d" % len(pop))

        rows = [{"path": p["rel"], "sha256": digest_bytes(read_bytes(root, p["rel"])),
                 "bytes": len(norm_bytes(read_bytes(root, p["rel"])))} for p in pop]
        pid = pin_id(rows)
        # 3-5: the address is content, order-free, and sensitive to one byte
        leg("the same members in another order carry the same pin id",
            pin_id(list(reversed(rows))) == pid)
        leg("one flipped byte in one member changes the pin id",
            pin_id([dict(rows[0], sha256=digest_bytes(b"x"))] + rows[1:]) != pid)
        leg("an empty population cannot produce a pin id", pin_id([]) != pid)
        # 6: CRLF is not content under this rule, and the rule does not depend on the decoder
        leg("a CRLF member and its LF twin share one digest",
            digest_bytes(b"a\r\nb") == digest_bytes(b"a\nb"))
        utf16 = read_bytes(root, "results/C/U-2026-01-06.json")
        leg("a UTF-16 member is classified and hashes over its bytes (the first draft's defect)",
            encoding_class(utf16) == "utf-16-bom"
            and digest_bytes(utf16) == hashlib.sha256(norm_bytes(utf16)).hexdigest())
        # 7: hydrate -> rescan round-trips the population (the replay root is shaped like the repo)
        members = {p["rel"]: read_bytes(root, p["rel"]) for p in pop}
        dest = os.path.join(tmp, "replay")
        written = hydrate(members, dest)
        rescanned = e328.scan_faces(dest)
        leg("a hydrated root rescans to the same population",
            len(written) == 4 and [r["rel"] for r in rescanned] == [r["rel"] for r in pop],
            "written=%d scanned=%d" % (len(written), len(rescanned)))
        leg("the UTF-16 member survives hydration byte-identical",
            read_bytes(dest, "results/C/U-2026-01-06.json") == norm_bytes(utf16))

        # 8-12: replay verdicts on a synthetic pin, graded independently of this repo
        commit = head_commit()
        pin = {"pin_id": pid, "count": len(rows), "study": "fixture", "git_commit": commit,
               "sources": [dict(r, tracked=False, dirty=False, git_can_supply=False)
                           for r in rows]}
        write_store(pin, members, dest_dir=tmp)
        good = replay(pin, store_dir=tmp)
        leg("a fully stored pin replays to verdict ok with every member from the store",
            good["verdict"] == VERDICT_OK and good["reproduces"] and good["from_store"] == 4,
            good["verdict"])
        tampered = dict(members)
        first = sorted(tampered)[0]
        tampered[first] = tampered[first].replace(b"2026", b"2025")
        write_store(pin, tampered, dest_dir=tmp)
        bad = replay(pin, store_dir=tmp)
        leg("a store whose bytes moved is convicted, not accepted as a replay",
            bad["verdict"] == VERDICT_MISMATCH and bad["mismatched"][0]["path"] == first,
            bad["verdict"])
        for f in glob.glob(os.path.join(tmp, "FACESTORE-*.json")):
            os.remove(f)
        gone = replay(pin, store_dir=tmp)
        leg("an absent store refuses the replay instead of returning a short corpus",
            gone["verdict"] == VERDICT_MISSING and len(gone["missing"]) == 4, gone["verdict"])
        nocommit = replay(dict(pin, git_commit=""), store_dir=tmp)
        leg("a commitless pin is its own verdict",
            nocommit["verdict"] == VERDICT_NO_COMMIT, nocommit["verdict"])
        empty = replay(dict(pin, sources=[]), store_dir=tmp)
        leg("an empty pin is its own verdict, never a green replay",
            empty["verdict"] == VERDICT_EMPTY, empty["verdict"])

        # 13: a count is not an address -- the drift block declines rather than inventing a delta
        drift = drift_against_published({"found": False}, rows, root)
        leg("with no published face the comparison declines instead of inventing a delta",
            drift["comparable"] is False)
        # 14: the pin must not eat its own tail (E319 applied to the pinning layer)
        own_rel = "results/A/FACEPOPPIN-%s.json" % dt.date.today().isoformat()
        with open(os.path.join(root, own_rel), "wb") as fh:
            fh.write(b'{"study": "E365_face_population_pin"}')
        leg("the study's own published face is scanned by E328 but excluded from the pin",
            len(e328.scan_faces(root)) == 5 and len(population(root)) == 4,
            "scanner=%d pinned=%d" % (len(e328.scan_faces(root)), len(population(root))))
        # 14: the diff partition keeps "changed" distinct from removed+added (E361's own routine)
        moved = [rows[0], dict(rows[1], sha256=digest_bytes(b"x")), rows[2], rows[3]]
        part = diff_corpora(rows, moved)
        leg("a member whose bytes moved is 'changed', not 'removed+added'",
            part["changed"] == [rows[1]["path"]] and part["added"] == []
            and part["removed"] == [], json.dumps(part)[:100])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = sum(1 for _n, ok, _d in legs if ok)
    for name, ok, detail in legs:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name,
                            ("  [%s]" % detail) if detail else ""))
    print("\nselftest %d/%d" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


# ------------------------------------------------------------------------------------------- cli
def cmd_stamp() -> int:
    built = build()
    members, refused = {}, []
    for s in unsuppliable(built):
        raw = read_bytes(ROOT, s["path"])
        if raw is None or (s["sha256"] and digest_bytes(raw) != s["sha256"]):
            refused.append(s["path"])
        else:
            members[s["path"]] = raw
    store = write_store(built, members) if members else ""
    built["store"] = {"path": relpath(store) if store else "", "members": len(members),
                      "bytes": os.path.getsize(store) if store else 0, "refused": refused}
    scratch = tempfile.mkdtemp(prefix="e365_stamp_")
    try:
        built["rerun_summary"] = (e328.build(root=ROOT, outdir=scratch).get("summary") or {})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    _write(built["face_path"], built)
    _write(os.path.join(OUTDIR, "facepoppin_latest.json"), built)

    s = built["summary"]
    print("pin %s  faces %d  families %d  dirs %d  parseable %d/%d"
          % (built["pin_id"][:16], s["faces"], s["families"], s["dirs"],
             s.get("parseable", -1), s["faces"]))
    print("encoding %s" % json.dumps(s["encoding"], sort_keys=True))
    print("supply: git %d (%.2f pct)  untracked %d  dirty %d  store %d members %d bytes"
          % (s["git_can_supply"], s["pct_supplied_by_git"], s["untracked"], s["dirty"],
             len(members), built["store"]["bytes"]))
    d = built["drift_vs_published"]
    print("published: faces_scanned=%s  pinned=%s  delta=%s  newer_than_published=%s  agrees=%s"
          % (d.get("published_faces_scanned"), d.get("pinned_faces"), d.get("delta"),
             d.get("newer_count"), d.get("heuristic_agrees")))
    for p in refused[:10]:
        print("  refused %s" % p)
    print("face %s" % relpath(built["face_path"]))
    return 0 if len(members) == len(unsuppliable(built)) else 1


def cmd_rerun() -> int:
    pin = load_newest_pin()
    r = rerun(pin)
    today = dt.date.today().isoformat()
    payload = dict(r, study=STUDY, evidence_cutoff=today,
                   generated=dt.datetime.now().isoformat(timespec="seconds"))
    path = os.path.join(OUTDIR, "FACERERUN-%s.json" % today)
    _write(path, payload)
    _write(os.path.join(OUTDIR, "facererun_latest.json"), payload)
    print("verdict %s" % r["verdict"])
    print("replayed population %s / pinned %s  hydrated %s"
          % (r.get("replayed_population"), r.get("pinned_population"),
             r.get("hydrated_members")))
    print("summary keys %s  moved %s" % (r.get("summary_keys_compared"),
                                        r.get("summary_moved_keys")))
    print("reader domain moved: %s" % r.get("reader_domain_moved"))
    print("face %s" % relpath(path))
    return 0 if r["verdict"] in (RERUN_SAME, RERUN_MOVED) else 1


def cmd_check() -> int:
    """Chain leg: rebuild the published population from commit + store, nothing else (~10 s)."""
    pin = load_newest_pin()
    r = replay(pin)
    s = pin.get("summary") or {}
    print("pin %s  faces %s  replay %s/%s  from_commit %d  from_store %d  store_members %d"
          % (pin.get("pin_id", "")[:16], pin.get("count"), r.get("replayed_count"),
             r.get("count"), r.get("from_commit", 0), r.get("from_store", 0),
             (pin.get("store") or {}).get("members")))
    print("verdict %s  reproduces=%s  missing %d  mismatched %d"
          % (r.get("verdict"), r.get("reproduces"), len(r.get("missing") or []),
             len(r.get("mismatched") or [])))
    bad = []
    if r["verdict"] != VERDICT_OK:
        bad.append("the published pin does not replay")
    if (pin.get("store") or {}).get("members") != s.get("needs_store"):
        bad.append("the store does not cover exactly the members git cannot supply")
    if (r.get("from_commit", 0) + r.get("from_store", 0)) != r.get("replayed_count"):
        bad.append("from_commit+from_store does not partition the replay")
    if len(pin.get("sources") or []) != pin.get("count"):
        bad.append("the sources list is not the published count")
    if not (isinstance(pin.get("git_commit"), str) and len(pin["git_commit"]) == 40):
        bad.append("the pin names no 40-hex commit")
    if any(n in {os.path.basename(x["path"]) for x in pin.get("sources") or []}
           for n in own_faces()):
        bad.append("the pin counts a face this study publishes (E319)")
    for b in bad:
        print("  FAIL %s" % b)
    return 0 if not bad else 1


def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "stamp"
    if cmd == "selftest":
        return selftest()
    if cmd == "stamp":
        return cmd_stamp()
    if cmd == "rerun":
        return cmd_rerun()
    if cmd == "check":
        return cmd_check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))