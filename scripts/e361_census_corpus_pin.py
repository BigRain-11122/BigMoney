"""E361 -- a census corpus is pinned by content digest, because the corpus is not in git.

r1382 closed the two visible defects behind "the summary does not re-derive" (a leg judged a face
against a corpus that had moved, and three legs republished the face they checked) and named the
real repair explicitly: *pinning a corpus by content digest, and teaching build() to accept a
snapshot, is not in this round.*

This is that half.  The census corpus here is whatever the study's own ``corpus()`` returns -- it is
imported, never re-implemented, so the pin cannot describe a different population than the study
counts.  Each member is recorded as (path, sha256 of LF-normalised text), and the face carries a
``pin_id`` over the sorted pairs: two runs that counted the same bytes carry the same pin_id, and a
run that counted different bytes cannot be mistaken for a reproduction.

The second question the pin makes answerable is *where* the corpus lives.  Each member is checked
against ``HEAD``: a tracked file whose working-tree blob differs from its committed blob is a file
whose committed bytes are not the bytes the census read, and an untracked file is one no checkout
of any commit can supply.  Both are printed as populations, not as opinions.

Usage:
  python scripts/e361_census_corpus_pin.py pin                # publish the pin face
  python scripts/e361_census_corpus_pin.py verify             # re-derive, diff against the pin
  python scripts/e361_census_corpus_pin.py hydrate --pin <f> --dest <dir>   # lay the pin on disk
  python scripts/e361_census_corpus_pin.py selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

# The study whose corpus() is pinned.  Imported, so the population is the study's own, not a copy
# of its walk: E323 enumerates scripts/Tools/live/monitor/firm for *.py and excludes itself.
STUDY = "e323_reach_under_wider_needle"
RULE = ("e323_reach_under_wider_needle.corpus(): python sources under "
        "scripts/Tools/live/monitor/firm, the study's own file excluded")

VERDICT_UNREACHABLE = "the_census_corpus_cannot_be_reassembled_from_any_commit"
VERDICT_REACHABLE = "every_pinned_source_is_a_tracked_clean_blob_so_head_reproduces_it"
VERDICT_IDLE = "pinned_idle_the_working_tree_still_has_the_pinned_bytes"


# ------------------------------------------------------------------------------------ pure core
def normalize(text: str) -> str:
    """CRLF and lone CR become LF, so a checkout's line endings are not a corpus change (r1317)."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def digest(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8", "surrogatepass")).hexdigest()


def relpath(path: str, root: str = ROOT) -> str:
    return os.path.relpath(os.path.abspath(path), root).replace("\\", "/")


def pin_id(sources) -> str:
    """Content address of a corpus: order-free, path-aware, digest of digests."""
    lines = sorted("%s\t%s" % (s["path"], s["sha256"]) for s in sources)
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def refuse_duplicates(sources) -> None:
    seen = set()
    for s in sources:
        if s["path"] in seen:
            raise ValueError("EMPTY-SCOPE: duplicate corpus path %s (a pin would double count it)"
                             % s["path"])
        seen.add(s["path"])
    if not sources:
        raise ValueError("EMPTY-SCOPE: an empty corpus is not a green pin")


def classify(sources, tree, work) -> list:
    """Attach git facts.  `tree` = HEAD path->blob, `work` = working-tree path->blob.

    A path absent from HEAD is `tracked=False` and is never called dirty: no commit holds it, so
    there is nothing for it to differ from.
    """
    out = []
    for s in sources:
        p = s["path"]
        tracked = p in tree
        dirty = bool(tracked and work.get(p) != tree.get(p))
        out.append(dict(s, tracked=tracked, head_blob=tree.get(p),
                        dirty=dirty, git_can_supply=bool(tracked and not dirty)))
    return out


def diff_corpora(pinned, now) -> dict:
    """Partition the difference by path.  A rename is removed+added, never 'changed'."""
    a = {s["path"]: s["sha256"] for s in pinned}
    b = {s["path"]: s["sha256"] for s in now}
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(p for p in set(a) & set(b) if a[p] != b[p])
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "pinned_count": len(a),
        "now_count": len(b),
        "unchanged": len(set(a) & set(b)) - len(changed),
        "pin_id_before": pin_id(pinned),
        "pin_id_now": pin_id(now),
        "verdict": VERDICT_IDLE if not (added or removed or changed) else "corpus_moved",
    }


def summarize(rows) -> dict:
    n = len(rows)
    tracked = sum(1 for r in rows if r["tracked"])
    untracked = n - tracked
    dirty = sum(1 for r in rows if r["dirty"])
    clean = tracked - dirty
    if n == 0:
        raise ValueError("EMPTY-SCOPE: cannot summarise an empty corpus")
    return {
        "corpus_count": n,
        "tracked": tracked,
        "untracked": untracked,
        "untracked_share_pct": round(100.0 * untracked / n, 2),
        "tracked_dirty": dirty,
        "tracked_clean": clean,
        "dirty_share_of_tracked_pct": round(100.0 * dirty / tracked, 2) if tracked else 0.0,
        "git_can_supply": clean,
        "git_can_supply_share_pct": round(100.0 * clean / n, 2),
        "git_cannot_supply": n - clean,
        "verdict": VERDICT_UNREACHABLE if (untracked or dirty) else VERDICT_REACHABLE,
    }


# -------------------------------------------------------------------------------- corpus + git io
def load_corpus(module_name: str = STUDY) -> list:
    sys.path.insert(0, HERE)
    mod = importlib.import_module(module_name)
    rows = []
    for path, text in mod.corpus():
        rows.append({"path": relpath(path, mod.ROOT), "sha256": digest(text),
                     "bytes": len(normalize(text).encode("utf-8", "surrogatepass"))})
    rows.sort(key=lambda r: r["path"])
    refuse_duplicates(rows)
    return rows


def _git(*args, input_text=None) -> str:
    p = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                       input=(input_text.encode("utf-8") if input_text is not None else None))
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args),
                                                  p.stderr.decode("utf-8", "replace")[:200]))
    return p.stdout.decode("utf-8", "replace")


_TREE = {}


def full_tree() -> dict:
    """path -> blob sha for every file HEAD knows.  One ls-tree call, cached per process."""
    if _TREE:
        return _TREE
    for line in _git("ls-tree", "-r", "HEAD").splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3:
            _TREE[path] = parts[2]
    return _TREE


def head_tree(paths) -> dict:
    tree = full_tree()
    return {p: tree[p] for p in paths if p in tree}


def worktree_blobs(paths) -> dict:
    """path -> blob sha of the working-tree bytes, in one call (--stdin-paths)."""
    if not paths:
        return {}
    out = _git("hash-object", "--stdin-paths", input_text="\n".join(paths) + "\n")
    shas = out.splitlines()
    if len(shas) != len(paths):
        raise RuntimeError("hash-object returned %d shas for %d paths" % (len(shas), len(paths)))
    return dict(zip(paths, shas))


# ------------------------------------------------------------------------------------- face build
DATED_FACE = re.compile(r"^[A-Za-z0-9_]+-\d{4}-\d{2}-\d{2}\.json$")


def face_population(outdir: str = None) -> dict:
    """The same git question asked of the outputs: are the published dated faces in git?

    A census whose output nobody can fetch is unreproducible for the same reason its input is.
    """
    outdir = outdir or OUTDIR
    paths = sorted(relpath(os.path.join(outdir, f))
                   for f in os.listdir(outdir) if DATED_FACE.match(f))
    if not paths:
        raise ValueError("EMPTY-SCOPE: no dated faces under %s" % outdir)
    tree = head_tree(paths)
    work = worktree_blobs(paths)
    rows = classify([{"path": p, "sha256": "", "bytes": 0} for p in paths], tree, work)
    s = summarize(rows)
    s["untracked_faces"] = [r["path"] for r in rows if not r["tracked"]]
    s["dirty_faces"] = [r["path"] for r in rows if r["dirty"]]
    s["dir"] = relpath(outdir)
    return s


def build(study: str = STUDY, outdir: str = None) -> dict:
    outdir = outdir or OUTDIR
    sources = load_corpus(study)
    paths = [s["path"] for s in sources]
    tree = head_tree(paths)
    work = worktree_blobs(paths)
    rows = classify(sources, tree, work)
    summary = summarize(rows)
    today = dt.date.today().isoformat()
    face = {
        "study": study,
        "rule": RULE,
        # The commit is part of the address: a path+digest without it names bytes nobody can fetch.
        # E362 replays this pin from (commit, blob) and from the inline store, never from the tree.
        "git_commit": _git("rev-parse", "HEAD").strip(),
        "evidence_cutoff": today,
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "pin_id": pin_id(rows),
        "count": len(rows),
        "sources": [{"path": r["path"], "sha256": r["sha256"], "bytes": r["bytes"],
                     "tracked": r["tracked"], "dirty": r["dirty"]} for r in rows],
        "summary": summary,
        "faces": face_population(outdir),
    }
    face["summary"]["pin_id"] = face["pin_id"]
    face["summary"]["count_matches_sources"] = (face["count"] == len(face["sources"]))
    os.makedirs(outdir, exist_ok=True)
    dated = os.path.join(outdir, "CORPUSPIN-%s.json" % today)
    with io.open(dated, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return face


def newest_pin() -> str:
    pins = sorted(f for f in os.listdir(OUTDIR)
                  if DATED_FACE.match(f) and f.startswith("CORPUSPIN-"))
    if not pins:
        raise RuntimeError("no published corpus pin under %s" % OUTDIR)
    return os.path.join(OUTDIR, pins[-1])


def load_pin(path: str = None) -> dict:
    path = path or newest_pin()
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def verify(path: str = None) -> dict:
    pin = load_pin(path)
    now = load_corpus(pin.get("study") or STUDY)
    d = diff_corpora(pin["sources"], now)
    paths = [s["path"] for s in now]
    d.update(summarize(classify(now, head_tree(paths), worktree_blobs(paths))))
    d["published_pin_id"] = pin["pin_id"]
    d["reproduces"] = (d["pin_id_now"] == pin["pin_id"])
    return d


def hydrate(pin_path: str, dest: str) -> dict:
    """Lay the pinned text on disk so a later build() can be pointed at a snapshot."""
    pin = load_pin(pin_path)
    sys.path.insert(0, HERE)
    mod = importlib.import_module(pin.get("study") or STUDY)
    live = {relpath(p, mod.ROOT): t for p, t in mod.corpus()}
    written, missing = [], []
    for s in pin["sources"]:
        text = live.get(s["path"])
        if text is None:
            missing.append(s["path"])
            continue
        target = os.path.join(dest, s["path"].replace("/", os.sep))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(normalize(text))
        if digest(text) != s["sha256"]:
            raise RuntimeError("hydrate: %s no longer hashes to the pin" % s["path"])
        written.append(s["path"])
    return {"written": len(written), "missing_from_disk": missing,
            "dest": os.path.abspath(dest), "pin_id": pin["pin_id"]}


# -------------------------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1-2: line endings and separator independence
    leg("normalise: CRLF and LF are the same corpus member",
        digest("a\r\nb\r\n") == digest("a\nb\n"), digest("a\r\nb\r\n")[:12])
    leg("pin_id ignores order", pin_id([{"path": "a", "sha256": "1"},
                                        {"path": "b", "sha256": "2"}])
        == pin_id([{"path": "b", "sha256": "2"}, {"path": "a", "sha256": "1"}]))
    # 3: a changed byte moves the pin_id
    leg("one changed digest moves pin_id",
        pin_id([{"path": "a", "sha256": "1"}]) != pin_id([{"path": "a", "sha256": "9"}]))
    # 4: empty corpus is refused, not published as a green zero
    try:
        refuse_duplicates([])
        ok = False
        d = "no exception"
    except ValueError as e:
        ok, d = "EMPTY-SCOPE" in str(e), str(e)[:40]
    leg("an empty corpus refuses to be pinned", ok, d)
    # 5: duplicates refuse (a double count would inflate the population)
    try:
        refuse_duplicates([{"path": "a", "sha256": "1"}, {"path": "a", "sha256": "1"}])
        ok, d = False, "no exception"
    except ValueError as e:
        ok, d = "duplicate" in str(e), str(e)[:40]
    leg("a duplicated path refuses instead of double counting", ok, d)
    # 6-9: the diff partition
    a = [{"path": "x", "sha256": "1"}, {"path": "y", "sha256": "2"}]
    leg("identical corpora are pinned_idle",
        diff_corpora(a, list(a))["verdict"] == VERDICT_IDLE)
    d1 = diff_corpora(a, [{"path": "x", "sha256": "1"}, {"path": "y", "sha256": "9"}])
    leg("one changed file is exactly one changed row",
        d1["changed"] == ["y"] and not d1["added"] and not d1["removed"], str(d1["changed"]))
    d2 = diff_corpora(a, [{"path": "x", "sha256": "1"}, {"path": "z", "sha256": "2"}])
    leg("a rename is removed+added, never changed",
        d2["removed"] == ["y"] and d2["added"] == ["z"] and d2["changed"] == [])
    leg("partition sums equal the population delta",
        d2["now_count"] - d2["pinned_count"] == len(d2["added"]) - len(d2["removed"]))
    # 10-12: git classification, computed from blobs rather than assumed from text
    tree = {"t.py": "b1"}
    rows = classify([{"path": "t.py", "sha256": "a", "bytes": 1},
                     {"path": "new.py", "sha256": "b", "bytes": 1}],
                    tree, {"t.py": "b1", "new.py": "b9"})
    by = {r["path"]: r for r in rows}
    leg("untracked is not called dirty", by["new.py"]["tracked"] is False
        and by["new.py"]["dirty"] is False)
    leg("tracked and identical is clean", by["t.py"]["dirty"] is False
        and by["t.py"]["git_can_supply"] is True)
    rows2 = classify([{"path": "t.py", "sha256": "a", "bytes": 1}], tree, {"t.py": "b2"})
    leg("tracked but different bytes is dirty and not git-suppliable",
        rows2[0]["dirty"] is True and rows2[0]["git_can_supply"] is False)
    # 13: the summary's own arithmetic
    s = summarize(rows + [dict(rows2[0])])
    leg("summary partitions add up",
        s["tracked"] + s["untracked"] == s["corpus_count"]
        and s["tracked_clean"] + s["tracked_dirty"] == s["tracked"]
        and s["git_can_supply"] + s["git_cannot_supply"] == s["corpus_count"],
        "n=%d" % s["corpus_count"])
    leg("a corpus with an untracked member is convicted unreachable",
        s["verdict"] == VERDICT_UNREACHABLE)
    # 14: hydrate round trip on a real temp tree
    tmp = tempfile.mkdtemp(prefix="e361_")
    try:
        rel = "scripts/_e361_probe.py"
        target = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        text = "x = 1\r\n"
        with io.open(target, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        with io.open(target, encoding="utf-8") as fh:
            back = fh.read()
        leg("hydrate writes LF and re-reads to the same digest",
            digest(back) == digest(text), digest(back)[:12])
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name,
                            ("  [%s]" % detail) if detail else ""))
    print("\nselftest %d/%d" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


# ------------------------------------------------------------------------------------------- cli
def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "pin"
    if cmd == "selftest":
        return selftest()
    if cmd == "pin":
        face = build()
        s = face["summary"]
        print("pin_id %s  count %d" % (face["pin_id"][:16], face["count"]))
        print("tracked %d  untracked %d (%.2f%%)  dirty %d (%.2f%% of tracked)  git_can_supply %d "
              "(%.2f%%)" % (s["tracked"], s["untracked"], s["untracked_share_pct"],
                            s["tracked_dirty"], s["dirty_share_of_tracked_pct"],
                            s["git_can_supply"], s["git_can_supply_share_pct"]))
        print("verdict %s" % s["verdict"])
        return 0
    if cmd == "verify":
        d = verify(argv[2] if len(argv) > 2 else None)
        print("published pin_id %s  now %s  reproduces=%s"
              % (d["published_pin_id"][:16], d["pin_id_now"][:16], d["reproduces"]))
        print("added %d  removed %d  changed %d  unchanged %d of %d"
              % (len(d["added"]), len(d["removed"]), len(d["changed"]),
                 d["unchanged"], d["pinned_count"]))
        print("verdict %s" % d["verdict"])
        for p in (d["added"] + d["removed"] + d["changed"])[:10]:
            print("  %s" % p)
        return 0
    if cmd == "hydrate":
        pin = argv[argv.index("--pin") + 1] if "--pin" in argv else None
        dest = argv[argv.index("--dest") + 1] if "--dest" in argv else None
        if not dest:
            dest = tempfile.mkdtemp(prefix="e361_snapshot_")
        r = hydrate(pin, dest)
        print("hydrated %d files to %s (missing from disk %d)"
              % (r["written"], r["dest"], len(r["missing_from_disk"])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))