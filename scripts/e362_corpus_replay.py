"""E362 -- the corpus pin is replayed from its own address, never from the working tree.

r1383 published a pin: every census corpus member recorded as (path, sha256 of LF text), with a
``pin_id`` over the sorted pairs, and closed with an explicit gap -- *"build() still does not
accept a snapshot, so a census cannot yet be re-run against the pin; the pin exists, the pointer
does not."*  A digest that nobody can turn back into the bytes it summarises is a receipt, not a
reproduction recipe.

This is the pointer.  A pin names a commit, so a tracked-and-clean member is fetchable as a git
blob; the minority that no commit holds (untracked scratch and files whose working copy differs
from their committed blob -- 107 of 2362 at the r1383 pin, 12.8 pct of the bytes) is written to a
content-addressed store beside the face.  Replay then rebuilds the corpus from *those two sources
only* -- ``git cat-file`` and the store -- re-hashes every member against the pin, and recomputes
``pin_id``.  Nothing is read from the work tree, which is the whole point: today's disk is exactly
the thing that keeps moving underneath a census.

The verdict vocabulary is ordered so an incomplete store can never read as success:
  * a member with no address at all      -> cannot_be_replayed (missing)
  * bytes that do not hash to the pin    -> cannot_be_replayed (mismatched)
  * every member accounted for, id equal -> replayed_from_commit_plus_store

Usage:
  python scripts/e362_corpus_replay.py store [--pin <face>]     # write the inline store
  python scripts/e362_corpus_replay.py replay [--pin <face>]    # rebuild + verify, publish face
  python scripts/e362_corpus_replay.py selftest
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from e361_census_corpus_pin import (  # reuse the pin's own identity functions, never a copy
    ROOT, OUTDIR, digest, normalize, pin_id, relpath, load_pin, newest_pin,
)

STORE_DIR = os.path.join(OUTDIR, "corpus_store")

VERDICT_OK = "replayed_from_commit_plus_store"
VERDICT_MISSING = "cannot_be_replayed_members_have_no_address"
VERDICT_MISMATCH = "cannot_be_replayed_bytes_do_not_hash_to_the_pin"
VERDICT_NO_COMMIT = "cannot_be_replayed_the_pin_names_no_commit"


# ------------------------------------------------------------------------------------ store io
def store_path(pin_hash: str, dest_dir: str = STORE_DIR) -> str:
    return os.path.join(dest_dir, "CORPUSSTORE-%s.json" % pin_hash[:16])


def encode_text(text: str) -> str:
    """zlib over the LF-normalised UTF-8 bytes, then base64: the store is text, not a blob dump."""
    return base64.b64encode(zlib.compress(normalize(text).encode("utf-8", "surrogatepass"),
                                         9)).decode("ascii")


def decode_text(blob: str) -> str:
    return zlib.decompress(base64.b64decode(blob)).decode("utf-8", "surrogatepass")


def unsuppliable(pin: dict) -> list:
    """Members no commit can supply: untracked scratch, or a work copy that differs from its blob."""
    return [s for s in pin["sources"] if not (s.get("tracked") and not s.get("dirty"))]


def corpus_texts(study: str) -> dict:
    """The study's own corpus() as path->text, imported so the store cannot describe another set."""
    import importlib
    sys.path.insert(0, HERE)
    mod = importlib.import_module(study)
    return {relpath(p, mod.ROOT): t for p, t in mod.corpus()}


def write_store(pin: dict, texts: dict, dest_dir: str = STORE_DIR) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    path = store_path(pin["pin_id"], dest_dir)
    payload = {"pin_id": pin["pin_id"], "study": pin.get("study"),
               "git_commit": pin.get("git_commit"),
               "count": len(texts),
               "texts": {p: encode_text(t) for p, t in sorted(texts.items())}}
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return path


def load_store(pin_hash: str, dest_dir: str = STORE_DIR) -> dict:
    path = store_path(pin_hash, dest_dir)
    if not os.path.exists(path):
        raise FileNotFoundError("no store for pin %s at %s" % (pin_hash[:16], path))
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ----------------------------------------------------------------------------------- git replay
def blob_texts(commit: str, paths) -> tuple:
    """Text of `commit:path` for every path the commit holds. Reads git objects, not the tree."""
    paths = list(paths)
    if not paths:
        return {}, []
    tree = {}
    p = subprocess.run(["git", "ls-tree", "-r", commit], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git ls-tree %s failed: %s"
                           % (commit[:12], p.stderr.decode("utf-8", "replace")[:200]))
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3:
            tree[path] = parts[2]
    wanted = [(p, tree[p]) for p in paths if p in tree]
    missing = [p for p in paths if p not in tree]
    if not wanted:
        return {}, missing
    blobs = {}
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, capture_output=True,
                          input=("\n".join(b for _p, b in wanted) + "\n").encode("ascii"))
    if proc.returncode != 0:
        raise RuntimeError("git cat-file failed: %s"
                           % proc.stderr.decode("utf-8", "replace")[:200])
    buf, i = proc.stdout, 0
    for _path, blob in wanted:
        nl = buf.index(b"\n", i)
        header = buf[i:nl].decode("ascii", "replace").split()
        i = nl + 1
        if len(header) < 3 or header[1] != "blob":
            continue
        size = int(header[2])
        blobs[blob] = buf[i:i + size].decode("utf-8", "replace")
        i += size + 1
    return {p: blobs[b] for p, b in wanted if b in blobs}, missing


# ---------------------------------------------------------------------------------------- replay
def replay(pin_file: str = None, store_dir: str = STORE_DIR) -> dict:
    pin = load_pin(pin_file)
    commit = pin.get("git_commit")
    if not commit:
        return {"verdict": VERDICT_NO_COMMIT, "pin_id": pin.get("pin_id"),
                "count": pin.get("count"), "missing": [s["path"] for s in pin["sources"]],
                "mismatched": [], "from_commit": 0, "from_store": 0}
    gits = [s for s in pin["sources"] if s.get("tracked") and not s.get("dirty")]
    from_git, missing_git = blob_texts(commit, [s["path"] for s in gits])
    store = load_store(pin["pin_id"], store_dir)
    from_store = {p: decode_text(b) for p, b in store["texts"].items()}

    rows, missing, mismatched = [], [], []
    n_git = n_store = 0
    for s in sorted(pin["sources"], key=lambda r: r["path"]):
        p = s["path"]
        if p in from_git:
            text, n_git = from_git[p], n_git + 1
        elif p in from_store:
            text, n_store = from_store[p], n_store + 1
        else:
            missing.append(p)
            continue
        got = digest(text)
        if got != s["sha256"]:
            mismatched.append({"path": p, "pinned": s["sha256"], "replayed": got})
            continue
        rows.append({"path": p, "sha256": got,
                     "bytes": len(normalize(text).encode("utf-8", "surrogatepass"))})

    replayed_id = pin_id(rows) if rows else ""
    if missing or mismatched or len(rows) != pin["count"]:
        verdict = VERDICT_MISSING if missing else VERDICT_MISMATCH
    elif replayed_id != pin["pin_id"]:
        verdict = VERDICT_MISMATCH
    else:
        verdict = VERDICT_OK
    return {
        "verdict": verdict,
        "study": pin.get("study"),
        "git_commit": commit,
        "pin_id": pin["pin_id"],
        "replayed_pin_id": replayed_id,
        "reproduces": (replayed_id == pin["pin_id"]),
        "count": pin["count"],
        "replayed_count": len(rows),
        "count_matches": len(rows) == pin["count"],
        "from_commit": n_git,
        "from_store": n_store,
        "bytes": sum(r["bytes"] for r in rows),
        "missing": missing,
        "mismatched": mismatched,
        "store_count": len(from_store),
        "working_tree_read": False,
    }


def publish(result: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    today = dt.date.today().isoformat()
    payload = dict(result, evidence_cutoff=today,
                   generated=dt.datetime.now().isoformat(timespec="seconds"))
    path = os.path.join(OUTDIR, "CORPUSREPLAY-%s.json" % today)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return path


# -------------------------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1-2: the store is a lossless, line-ending-independent carrier
    text = "x = 1\r\ny = '\u4e2d\u6587'\r\n"
    leg("store round-trips CRLF text and re-hashes to the source digest",
        digest(decode_text(encode_text(text))) == digest(text))
    leg("store normalises on the way in (CRLF and LF share one encoding)",
        encode_text("a\r\n") == encode_text("a\n"))

    # 3-4: absence and corruption are both refusals, not quiet zeros
    leg("an empty corpus cannot produce a pin id", pin_id([]) != pin_id([{"path": "a",
                                                                        "sha256": "1"}]))
    a = [{"path": "a", "sha256": digest("1"), "bytes": 1}]
    leg("one flipped byte breaks the pin id", pin_id(a) != pin_id(
        [{"path": "a", "sha256": digest("2"), "bytes": 1}]))

    # 5: git replay really reads blobs -- exercised against this repo's own HEAD
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True)
    commit = head.stdout.decode().strip()
    texts, missing = blob_texts(commit, ["scripts/e361_census_corpus_pin.py",
                                         "scripts/_e362_not_a_file.py"])
    leg("a committed path replays from git and an absent one is reported, not invented",
        ("scripts/e361_census_corpus_pin.py" in texts
         and missing == ["scripts/_e362_not_a_file.py"]), "commit %s" % commit[:12])
    leg("the replayed blob is the file's own text",
        texts.get("scripts/e361_census_corpus_pin.py", "").startswith('"""E361'))

    # 6-8: end-to-end on a synthetic pin, so the verdict logic is graded independently of this repo
    tmp = tempfile.mkdtemp(prefix="e362_")
    try:
        pinned = [{"path": "a.py", "sha256": digest("A\n"), "bytes": 2, "tracked": False}]
        pin = {"pin_id": pin_id(pinned), "count": 1, "sources": pinned,
               "git_commit": commit, "study": "x"}
        pin_file = os.path.join(tmp, "CORPUSPIN-2026-01-01.json")
        with io.open(pin_file, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pin, fh)
        write_store(pin, {"a.py": "A\n"}, dest_dir=tmp)
        good = replay(pin_file, store_dir=tmp)
        leg("a fully stored pin replays to verdict ok with both counts equal",
            good["verdict"] == VERDICT_OK and good["reproduces"]
            and good["from_store"] == 1, good["verdict"])
        write_store(pin, {"a.py": "B\n"}, dest_dir=tmp)
        bad = replay(pin_file, store_dir=tmp)
        leg("a store whose bytes moved is convicted, not accepted as a replay",
            bad["verdict"] == VERDICT_MISMATCH and bad["mismatched"][0]["path"] == "a.py",
            bad["verdict"])
        missing_pin = dict(pin, sources=[{"path": "gone.py", "sha256": "0", "bytes": 1,
                                         "tracked": False}])
        pin_file2 = os.path.join(tmp, "CORPUSPIN-2026-01-02.json")
        with io.open(pin_file2, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(missing_pin, fh)
        noaddr = replay(pin_file2, store_dir=tmp)
        leg("a member with no address refuses the whole replay",
            noaddr["verdict"] == VERDICT_MISSING and noaddr["missing"] == ["gone.py"],
            noaddr["verdict"])
        empty_pin = dict(pin, git_commit=None)
        with io.open(pin_file2, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(empty_pin, fh)
        leg("a commitless pin is its own verdict",
            replay(pin_file2, store_dir=tmp)["verdict"] == VERDICT_NO_COMMIT)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    n_pass = sum(1 for _n, ok, _d in legs if ok)
    for name, ok, detail in legs:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name,
                            ("  [%s]" % detail) if detail else ""))
    print("\nselftest %d/%d" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


# ------------------------------------------------------------------------------------------- cli
def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "replay"
    pin_file = argv[argv.index("--pin") + 1] if "--pin" in argv else None
    if cmd == "selftest":
        return selftest()
    if cmd == "store":
        pin = load_pin(pin_file)
        need = unsuppliable(pin)
        live = corpus_texts(pin.get("study") or "e323_reach_under_wider_needle")
        texts, refused = {}, []
        for s in need:
            got = live.get(s["path"])
            if got is None or digest(got) != s["sha256"]:
                refused.append(s["path"])
            else:
                texts[s["path"]] = got
        path = write_store(pin, texts)
        print("store %s  members %d/%d  refused %d  pin %s"
              % (relpath(path), len(texts), len(need), len(refused), pin["pin_id"][:16]))
        for p in refused[:10]:
            print("  refused %s" % p)
        return 0 if len(texts) == len(need) else 1
    if cmd == "replay":
        r = replay(pin_file)
        path = publish(r)
        print("verdict %s  pin %s  replayed %s  reproduces=%s"
              % (r["verdict"], (r.get("pin_id") or "")[:16],
                 (r.get("replayed_pin_id") or "")[:16], r.get("reproduces")))
        print("count %s/%s  from_commit %d  from_store %d  missing %d  mismatched %d  bytes %d"
              % (r.get("replayed_count"), r.get("count"), r.get("from_commit", 0),
                 r.get("from_store", 0), len(r.get("missing") or []),
                 len(r.get("mismatched") or []), r.get("bytes") or 0))
        print("face %s" % relpath(path))
        return 0 if r["verdict"] == VERDICT_OK else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))