"""Round 1278: land bm-b's side blood line onto origin/main by bounded tree merge.

Design
------
base tree      = origin/main (nothing of theirs is reverted)
overlay        = files changed on our side since the merge base and NOT touched
                 on main since (167 files: our E-cards, digests, chain, faces)
allowlist      = append-only docs merged by block/line union
                 (CODELY.md, knowledge/METHODOLOGY_ASSETS.md)
everything else= origin-verbatim (bm-c's later work wins)

Result commit has two parents (HEAD, origin/main) so both lines are recorded as
merged without replaying 57 commits through the promisor lazy fetch.

Usage: python Tools/bloodline_land.py [--dry-run|--commit]

Proven r1278: landed 167 line-unique files + 22 method cards on main as
260d8f7a0 without a single replayed commit.
"""
import os
import re
import subprocess
import sys
import tempfile

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
UNION_DOCS = [
    "CODELY.md",
    "knowledge/METHODOLOGY_ASSETS.md",
]


def git(*args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True, env=e)


def out(*args, env=None):
    r = git(*args, env=env)
    if r.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace")[:500]))
    return r.stdout.decode("utf-8", "replace")


def raw(*args, env=None):
    r = git(*args, env=env)
    if r.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace")[:500]))
    return r.stdout


def changed(rev, base):
    s = out("diff", "--name-only", "--diff-filter=ACMRD", base + ".." + rev)
    return set(x for x in s.splitlines() if x.strip())


def ls_tree(rev):
    """path -> (mode, sha)"""
    d = {}
    for line in out("ls-tree", "-r", rev).splitlines():
        meta, path = line.split("\t", 1)
        mode, typ, sha = meta.split()
        d[path] = (mode, sha)
    return d


def hash_object(data):
    # temp file (binary safe, predictable); never pipe to hash-object --stdin
    # because an inherited stdin makes the call block forever
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        return out("hash-object", "-w", tmp).strip()
    finally:
        os.unlink(tmp)


def union_codely(origin_txt, head_txt):
    o = origin_txt.splitlines()
    seen = set(o)
    add = [l for l in head_txt.splitlines() if l.strip() and l not in seen]
    if not add:
        return origin_txt
    if not origin_txt.endswith("\n"):
        origin_txt += "\n"
    return origin_txt + "\n" + "\n".join(add) + "\n"


def union_methodology(origin_txt, head_txt):
    o_ids = set(int(m) for m in re.findall(r"^### E(\d+)", origin_txt, re.M))
    blocks = re.split(r"(?m)^(?=### E\d+)", head_txt)
    add = []
    for b in blocks:
        m = re.match(r"### E(\d+)", b)
        if not m:
            continue
        if int(m.group(1)) not in o_ids and b.strip():
            add.append(b.rstrip() + "\n")
    if not add:
        return origin_txt
    if not origin_txt.endswith("\n"):
        origin_txt += "\n"
    return origin_txt + "\n" + "\n".join(add)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    mb = out("merge-base", "HEAD", "origin/main").strip()
    mine = changed("HEAD", mb)
    theirs = changed("origin/main", mb)
    overlay = sorted(mine - theirs)

    o_tree = ls_tree("origin/main")
    h_tree = ls_tree("HEAD")

    plan = []  # (mode, blob, path)
    missing = []
    for p in overlay:
        if p in UNION_DOCS:
            continue
        if p not in h_tree:
            missing.append(p)  # we deleted it -> keep origin's copy, be conservative
            continue
        plan.append((h_tree[p][0], h_tree[p][1], p))

    print("merge_base=%s" % mb)
    print("overlay=%d  planned=%d  skipped_missing_local=%d" % (len(overlay), len(plan), len(missing)))
    for p in missing:
        print("  SKIP(deleted-on-our-side) %s" % p)

    union_blobs = {}
    for p in UNION_DOCS:
        o_txt = out("show", "origin/main:" + p)
        h_txt = out("show", "HEAD:" + p)
        merged = union_codely(o_txt, h_txt) if p == "CODELY.md" else union_methodology(o_txt, h_txt)
        delta = len(merged) - len(o_txt)
        print("  UNION %s  origin=%d merged=%d delta=%+d chars" % (p, len(o_txt), len(merged), delta))
        union_blobs[p] = merged.encode("utf-8")

    if mode == "--dry-run":
        print("DRY-RUN: no objects written.")
        return

    # build index
    idx = os.path.join(REPO, ".git", "index.r1278")
    if os.path.exists(idx):
        os.unlink(idx)
    env = {"GIT_INDEX_FILE": idx}
    out("read-tree", "origin/main", env=env)
    for m, sha, p in plan:
        out("update-index", "--add", "--cacheinfo", "%s,%s,%s" % (m, sha, p), env=env)
    for p, data in union_blobs.items():
        sha = hash_object(data)
        mode = o_tree.get(p, ("100644",))[0]
        out("update-index", "--add", "--cacheinfo", "%s,%s,%s" % (mode, sha, p), env=env)
    # --missing-ok: without it write-tree verifies every index entry's blob and
    # in a blob:none clone that fires a lazy fetch of ~2000 upstream blobs.
    tree = out("write-tree", "--missing-ok", env=env).strip()
    print("merged_tree=%s" % tree)

    # verify
    new = ls_tree(tree)
    bad = [p for _, _, p in plan if new.get(p, ("", ""))[1] != dict((q, s) for _, s, q in plan)[p]]
    print("verify: tree_files=%d  overlay_present=%d/%d  mismatch=%d" % (len(new), len(plan) - len(bad), len(plan), len(bad)))
    dropped = [p for p in o_tree if p not in new]
    print("verify: origin_files_dropped=%d" % len(dropped))
    for p in dropped[:10]:
        print("   DROP", p)
    os.unlink(idx)
    print("TREE=%s" % tree)


if __name__ == "__main__":
    main()