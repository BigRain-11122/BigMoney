#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""surgery_commit.py -- build a commit from a BASE REV plus NAMED files, and refuse
to publish one that lost the tree.

Why this exists (F-20261027-03, report carried by fleet/inbox/MSG-20261027-2250-bm-a.md):
a closeout pushed group commit ``ceebc703`` -- message "order-bus receipts for bm-b",
two files -- whose tree held 2 entries against its parent's 3,494. Every guard stayed
quiet because ``write-tree``/``commit-tree`` bypass pre-commit and pre-push entirely and
``git status`` in the worktree was clean. A temporary index seeded from NOTHING instead
of ``read-tree <parent>`` produces exactly that shape, and it looks like a normal
two-file receipt commit.

The invariant this tool enforces: a surgical commit may only ever be
    parent tree  +  the paths you named  -  the paths you named for deletion
so "I only staged two files" can never mean "I published two files".

Usage
-----
  python Tools/surgery_commit.py --message "round 7: ..." \
      --take results/face.json --take scripts/x.py [--take ...] \
      [--delete path] [--max-deletions 0] [--base origin/main] [--repo .] \
      [--dry-run] [--push] [--json]

  python Tools/surgery_commit.py selftest

Exit codes: 0 ok / 1 refused (guard) / 2 mechanism failure.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GIT = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"


class Refused(Exception):
    """The commit would have lost the tree, or a named path is not what it claims."""


class Broken(Exception):
    """Mechanism failure (git missing, bad rev, write failed)."""


class _R(object):
    """git result with stdout/stderr decoded as UTF-8.

    ``text=True`` lets Python pick the locale codec, and on this box that is GBK:
    a single CJK path in ``ls-tree -z`` kills the reader thread, ``stdout`` comes
    back as None and the return code is still 0 -- a silent empty read that looks
    exactly like an empty tree. So the subprocess is captured as bytes and decoded
    here, with surrogateescape so a path round-trips byte for byte.
    """
    __slots__ = ("returncode", "stdout", "stderr")

    def __init__(self, cp):
        self.returncode = cp.returncode
        self.stdout = cp.stdout.decode("utf-8", "surrogateescape")
        self.stderr = cp.stderr.decode("utf-8", "surrogateescape")


def git(repo, *args, env=None, check=True):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = _R(subprocess.run([GIT, "-C", repo] + list(args),
                          capture_output=True, env=e))
    if check and r.returncode != 0:
        raise Broken("git %s failed rc=%d: %s"
                     % (" ".join(args), r.returncode, r.stderr.strip()[:400]))
    return r


def _rev(repo, ref):
    r = git(repo, "rev-parse", "--verify", ref + "^{commit}", check=False)
    if r.returncode != 0:
        raise Broken("cannot resolve %r to a commit" % ref)
    return r.stdout.strip()


def _tree_count(repo, rev):
    out = git(repo, "ls-tree", "-r", "--name-only", "-z", rev).stdout
    return len([p for p in out.split("\0") if p])


def _tree_blob(repo, rev, path):
    out = git(repo, "ls-tree", "-z", rev, "--", path).stdout
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, _, name = rec.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and name == path:
            return parts[2]
    return None


def _assert_tree_size(base_count, new_count, allowed_deletions):
    """The ceebc703 guard: a surgical commit may not shrink the tree beyond its budget."""
    allowed = int(allowed_deletions)
    if new_count < base_count - allowed:
        raise Refused(
            "tree would shrink from %d to %d file(s); this commit is allowed to "
            "delete at most %d. The index was probably seeded from nothing instead of "
            "read-tree <base> -- that is the ceebc703 shape (3494 -> 2)."
            % (base_count, new_count, allowed))
    return True


def build(repo, message, take=(), delete=(), base="origin/main",
          max_deletions=0, dry_run=False, push=False):
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        raise Broken("%s is not a git repository" % repo)
    base_sha = _rev(repo, base)
    base_count = _tree_count(repo, base_sha)

    # --- validate the named paths BEFORE touching any index -------------------
    take = [p.replace("\\", "/") for p in take]
    delete = [p.replace("\\", "/") for p in delete]
    blobs = {}
    for p in take:
        full = os.path.join(repo, p)
        if not os.path.isfile(full):
            raise Refused("--take %r is not a file in the worktree" % p)
        blobs[p] = git(repo, "hash-object", "-w", "--no-filters", "--", p).stdout.strip()
    for p in delete:
        if _tree_blob(repo, base_sha, p) is None:
            raise Refused("--delete %r does not exist at %s, so deleting it is a no-op "
                          "that would hide a typo" % (p, base))

    tmp = tempfile.mkdtemp(prefix="surgery-")
    idx = os.path.join(tmp, "index")
    env = {"GIT_INDEX_FILE": idx}
    try:
        # seeded from the BASE tree -- never from nothing
        git(repo, "read-tree", base_sha, env=env)
        # the temp index is applied in dry-run too: a dry run that skipped the
        # named paths would report the BASE tree's sizes and hide the very
        # shrink/delta the caller is asking about. Nothing is published either
        # way -- --dry-run only suppresses commit-tree.
        for p, sha in blobs.items():
            mode = "100755" if os.access(os.path.join(repo, p), os.X_OK) else "100644"
            git(repo, "update-index", "--add", "--replace", "--cacheinfo",
                "%s,%s,%s" % (mode, sha, p), env=env)
        for p in delete:
            git(repo, "update-index", "--force-remove", "--", p, env=env)
        tree = git(repo, "write-tree", env=env).stdout.strip()
        new_count = _tree_count(repo, tree)
        _assert_tree_size(base_count, new_count, max_deletions)

        # every named path must be exactly what we think it is in the new tree
        for p, sha in blobs.items():
            got = _tree_blob(repo, tree, p)
            if got != sha:
                raise Refused("%r landed as blob %s, expected %s (a filter rewrote it?)"
                              % (p, got, sha))
        for p in delete:
            if _tree_blob(repo, tree, p) is not None:
                raise Refused("%r was asked to be deleted and is still in the tree" % p)

        receipt = {"repo": repo, "base": base, "base_sha": base_sha,
                   "base_files": base_count, "tree": tree, "tree_files": new_count,
                   "taken": sorted(take), "deleted": sorted(delete),
                   "delta_files": new_count - base_count, "dry_run": dry_run}
        if dry_run:
            return receipt

        msgf = os.path.join(tmp, "msg")
        with open(msgf, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(message.rstrip() + "\n")
        sha = git(repo, "commit-tree", tree, "-p", base_sha, "-F", msgf).stdout.strip()
        receipt["commit"] = sha

        # post-commit, pre-push: the same guard, read off the real commit
        got = _tree_count(repo, sha)
        _assert_tree_size(base_count, got, max_deletions)

        if push:
            r = git(repo, "push", "origin", "%s:refs/heads/main" % sha, check=False)
            if r.returncode != 0:
                raise Broken("push refused (fast-forward required): %s"
                             % (r.stderr or r.stdout).strip()[:300])
            tip = git(repo, "ls-remote", "origin", "refs/heads/main").stdout.split()[0]
            if tip != sha:
                raise Broken("push reported success but origin/main is %s, not %s"
                             % (tip, sha))
            receipt["origin_main"] = tip
        return receipt
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- selftest

def _selftest():
    ok = tot = 0

    def chk(cond, label):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
            print("[PASS] %s" % label)
        else:
            print("[FAIL] %s" % label)

    def raises(fn, exc):
        try:
            fn()
        except exc:
            return True
        except Exception:
            return False
        return False

    chk(raises(lambda: _assert_tree_size(3494, 2, 0), Refused),
        "L1 the ceebc703 shape (3494 -> 2) is refused")
    chk(raises(lambda: _assert_tree_size(6, 4, 1), Refused),
        "L2 a shrink past the explicit budget is refused")
    chk(_assert_tree_size(6, 6, 0) and _assert_tree_size(6, 5, 1),
        "L3 a same-size tree and a budgeted deletion both pass")
    chk(raises(lambda: _assert_tree_size(6, 5, 0), Refused),
        "L4 an unbudgeted single deletion is refused (typos cannot hide)")

    tmp = tempfile.mkdtemp(prefix="surgery-selftest-")
    repo = os.path.join(tmp, "r")
    os.makedirs(repo)
    try:
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.email", "selftest@example.invalid")
        git(repo, "config", "user.name", "selftest")
        for name, body in (("a.txt", "a1\n"), ("b.txt", "b1\n"), ("c.txt", "c1\n")):
            with open(os.path.join(repo, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")

        with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("a2\n")
        with open(os.path.join(repo, "d.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("d1\n")
        before = git(repo, "status", "--porcelain").stdout

        dry = build(repo, "dry", take=["a.txt", "d.txt"], base="origin/main", dry_run=True)
        chk(dry["base_files"] == 3 and "commit" not in dry,
            "L5 dry-run reports the base size and writes no commit")

        rec = build(repo, "surgical", take=["a.txt", "d.txt"], base="origin/main")
        chk(rec["tree_files"] == 4 and rec["delta_files"] == 1,
            "L6 a two-path surgical commit keeps every other file in the tree")
        chk(_tree_blob(repo, rec["commit"], "b.txt") == _tree_blob(repo, rec["base_sha"], "b.txt")
            and _tree_blob(repo, rec["commit"], "c.txt")
            == _tree_blob(repo, rec["base_sha"], "c.txt"),
            "L7 untouched files carry their base blobs verbatim")
        chk(git(repo, "rev-parse", rec["commit"] + "^").stdout.strip() == rec["base_sha"],
            "L8 the commit's parent is the requested base, not the worktree HEAD")
        chk(git(repo, "status", "--porcelain").stdout == before,
            "L9 the worktree and the real index are untouched")

        rec2 = build(repo, "one file only", take=["d.txt"], base="origin/main")
        chk(rec2["tree_files"] == 4,
            "L10 taking only the new file still carries the base's other files")

        chk(raises(lambda: build(repo, "typo", take=["nope.txt"], base="origin/main"),
                   Refused),
            "L11 a --take path that is not in the worktree is refused")
        chk(raises(lambda: build(repo, "typo", delete=["nope.txt"], base="origin/main"),
                   Refused),
            "L12 a --delete path that is not in the base tree is refused")

        rec3 = build(repo, "with delete", delete=["c.txt"], base="origin/main",
                     max_deletions=1)
        chk(rec3["tree_files"] == 2 and _tree_blob(repo, rec3["commit"], "c.txt") is None,
            "L13 a budgeted deletion lands and the tree shrinks by exactly one")

        # L14: this repository is full of CJK paths, and the first cut of this tool
        # read `ls-tree -z` through the locale codec -- one CJK name made stdout
        # None while rc stayed 0, i.e. every tree counted as empty. The fixture is
        # ASCII, so only a fixture that looks like the real tree can catch it.
        with open(os.path.join(repo, "报告-é.txt"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write("cjk\n")
        rec4 = build(repo, "cjk path", take=["报告-é.txt"], base="origin/main")
        chk(_tree_blob(repo, rec4["commit"], "报告-é.txt") is not None
            and rec4["tree_files"] >= 3,
            "L14 a non-ASCII path is counted and lands byte for byte")
    except Exception as exc:  # noqa: BLE001 - a broken selftest must fail loudly
        chk(False, "selftest harness: %s: %s" % (type(exc).__name__, exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nselftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return _selftest()
    take, delete, msg, base, repo = [], [], None, "origin/main", HERE and \
        os.path.dirname(HERE)
    max_del, dry, push, as_json = 0, False, False, False
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--take":
            take.append(argv[i + 1]); i += 2
        elif a == "--delete":
            delete.append(argv[i + 1]); i += 2
        elif a == "--message":
            msg = argv[i + 1]; i += 2
        elif a == "--base":
            base = argv[i + 1]; i += 2
        elif a == "--repo":
            repo = argv[i + 1]; i += 2
        elif a == "--max-deletions":
            max_del = int(argv[i + 1]); i += 2
        elif a == "--dry-run":
            dry = True; i += 1
        elif a == "--push":
            push = True; i += 1
        elif a == "--json":
            as_json = True; i += 1
        else:
            print("unknown argument %r" % a, file=sys.stderr)
            return 2
    if not msg:
        print("--message is required (a surgical commit without a reason is not "
              "reviewable)", file=sys.stderr)
        return 2
    try:
        rec = build(repo, msg, take=take, delete=delete, base=base,
                    max_deletions=max_del, dry_run=dry, push=push)
    except Refused as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 1
    except Broken as exc:
        print("BROKEN: %s" % exc, file=sys.stderr)
        return 2
    if as_json:
        print(json.dumps(rec, ensure_ascii=False))
    else:
        print("surgery ok: %s (%d -> %d files, %+d)"
              % (rec.get("commit") or "dry-run", rec["base_files"],
                 rec["tree_files"], rec["delta_files"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))