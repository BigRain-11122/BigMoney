"""Tree-shrink tripwire: a commit must not silently lose most of the repo.

Why this exists (r1133 bm-a, live-fire P0): the group repo's tip ceebc703 was
built from a partial index, so its tree carried only the two receipt files it
meant to add and dropped the other 3,494 files -- docs/decisions.md,
docs/orders.md, all of cph4/. Nothing in the repo noticed; the damage was found
by a consumer that tried to read decisions.md and got "exists on disk, but not
in origin/main". A commit-tree built from an empty or partial index is invisible
to hooks (it bypasses pre-commit entirely) and produces a perfectly valid,
successfully pushed commit whose only symptom is a smaller tree.

The check is deliberately dumb and cheap: count files in a commit's tree and in
its first parent's tree. A drop larger than the allowed budget is a red flag,
because normal work never deletes thousands of files at once.

Usage
  python Tools/tree_shrink_guard.py check --repo <path> [--commits N]
                                          [--max-drop N] [--json]
  python Tools/tree_shrink_guard.py selftest

Exit codes: 0 clean, 1 shrink detected, 2 mechanism failure (git unreadable).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

DEFAULT_COMMITS = 20
DEFAULT_MAX_DROP = 0


def _git(repo: str, *args: str) -> str:
    p = subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.strip()}")
    return p.stdout


def file_count(repo: str, rev: str) -> int:
    """Number of blobs (not subtrees) in <rev>'s tree."""
    try:
        out = _git(repo, "ls-tree", "-r", "--name-only", rev)
    except RuntimeError as e:
        # A root commit has no parent to compare against; anything else is real.
        raise
    return len([ln for ln in out.splitlines() if ln.strip()])


def parents(repo: str, rev: str) -> list[str]:
    out = _git(repo, "rev-list", "--parents", "-n", "1", rev).strip().split()
    return out[1:]


def scan(repo: str, commits: int = DEFAULT_COMMITS,
         max_drop: int = DEFAULT_MAX_DROP, rev: str = "HEAD") -> dict:
    rows = []
    out = _git(repo, "rev-list", f"-n{commits}", rev).split()
    for sha in out:
        par = parents(repo, sha)
        if not par:
            rows.append({"commit": sha[:12], "files": file_count(repo, sha),
                         "parent": None, "drop": 0, "root": True,
                         "subject": _git(repo, "log", "-1", "--format=%s", sha).strip()[:120]})
            continue
        n_cur = file_count(repo, sha)
        n_par = file_count(repo, par[0])
        rows.append({"commit": sha[:12], "files": n_cur, "parent": par[0][:12],
                     "parent_files": n_par, "drop": n_par - n_cur,
                     "subject": _git(repo, "log", "-1", "--format=%s", sha).strip()[:120]})
    # A shrink that was later repaired is history, not a live defect: the tip
    # already carries the files again. Only an UNREPAIRED shrink is a failure,
    # otherwise the guard would stay red until the bad commit scrolled out of
    # the window and nobody would read it any more.
    tip_files = file_count(repo, rev)
    hits = []
    for r in rows:
        if r["drop"] <= max_drop:
            continue
        r = dict(r)
        r["repaired"] = tip_files >= r["parent_files"]
        hits.append(r)
    live = [r for r in hits if not r["repaired"]]
    return {"repo": os.path.abspath(repo), "scanned": len(rows), "rev": rev,
            "tip_files": tip_files, "max_drop_allowed": max_drop,
            "shrinks": hits, "unrepaired": live, "rows": rows,
            "clean": not live}


def cmd_check(args) -> int:
    try:
        res = scan(args.repo, args.commits, args.max_drop, args.rev)
    except RuntimeError as e:
        print(f"tree-shrink guard: mechanism failure: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        if res["clean"]:
            extra = (f" ({len(res['shrinks'])} repaired shrink(s) earlier in history)"
                     if res["shrinks"] else "")
            print(f"tree-shrink guard CLEAN: {res['scanned']} commit(s) in "
                  f"{res['repo']}, tip has {res['tip_files']} file(s), "
                  f"no unrepaired loss > {args.max_drop}{extra}")
        else:
            print(f"tree-shrink guard SHRINK: {len(res['unrepaired'])} commit(s) "
                  f"lost files and the tip has not recovered")
            for r in res["unrepaired"]:
                print(f"  {r['commit']} {r['parent_files']} -> {r['files']} "
                      f"(-{r['drop']}) {r['subject']}")
    return 0 if res["clean"] else 1


# --------------------------------------------------------------------------
# group face: the incident this guard exists for happened in the group repo, so
# the check must be able to reach it without hard-coding one machine's layout.
# --------------------------------------------------------------------------

def find_group_tree(start: str) -> str | None:
    """Walk up from <start> looking for a git repo that owns cph4/ (the group).

    Returns the repo path, or None when this machine has no group tree (bm-b and
    bm-c do not always carry one -- that is an honest no-op, not a failure).
    """
    cur = os.path.abspath(start)
    for _ in range(5):
        cur = os.path.dirname(cur)
        if not cur or cur == os.path.dirname(cur):
            break
        if os.path.isdir(os.path.join(cur, ".git")) and \
                os.path.isdir(os.path.join(cur, "cph4")):
            return cur
    return None


def cmd_check_group(args) -> int:
    repo = args.repo and os.path.abspath(args.repo) or find_group_tree(os.getcwd())
    if not repo:
        print("tree-shrink guard: no group tree on this machine -- honest no-op")
        return 0
    # prefer the fetched origin tip: the local branch may be behind the damage
    rev = "origin/main"
    try:
        _git(repo, "rev-parse", "--verify", rev)
    except RuntimeError:
        rev = "HEAD"
    try:
        res = scan(repo, args.commits, args.max_drop, rev)
    except RuntimeError as e:
        print(f"tree-shrink guard: mechanism failure on {repo}: {e}", file=sys.stderr)
        return 2
    if res["clean"]:
        tail = (f" ({len(res['shrinks'])} repaired shrink(s) in history)"
                if res["shrinks"] else "")
        print(f"tree-shrink guard CLEAN: group {rev} @ {repo}, {res['scanned']} "
              f"commit(s), tip {res['tip_files']} file(s){tail}")
    else:
        print(f"tree-shrink guard SHRINK: group {rev} @ {repo}")
        for r in res["unrepaired"]:
            print(f"  {r['commit']} {r['parent_files']} -> {r['files']} "
                  f"(-{r['drop']}) {r['subject']}")
    return 0 if res["clean"] else 1


# --------------------------------------------------------------------------
# selftest: a fixture repo where the second commit is built from a partial
# index, exactly reproducing the ceebc703 failure mode.
# --------------------------------------------------------------------------

def _fixture_repo(root: str) -> None:
    env = dict(os.environ, GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
               GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local")


def _g(repo: str, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", repo] + list(args), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=dict(os.environ, GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                 GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local",
                 GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull))
    if p.returncode != 0:
        raise RuntimeError(f"fixture git {' '.join(args)} rc={p.returncode}: {p.stderr}")
    return p.stdout.strip()


def cmd_selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="tsg-")
    legs: list[tuple[str, bool, str]] = []

    def leg(name: str, ok: bool, detail: str = "") -> None:
        legs.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        _g(repo, "init", "-q", "-b", "main")

        # L1: a normal commit does not trip the guard.
        for i in range(6):
            with open(os.path.join(repo, f"f{i}.txt"), "w", encoding="utf-8") as f:
                f.write(f"{i}\n")
        _g(repo, "add", "-A")
        _g(repo, "commit", "-qm", "six files")
        res = scan(repo, commits=1)
        leg("L1 clean history stays clean", res["clean"],
            f"files={res['rows'][0]['files']}")

        # L2: reproduce the failure -- commit-tree from a PARTIAL index.
        good = _g(repo, "rev-parse", "HEAD")
        idx = os.path.join(tmp, "partial.index")
        env = dict(os.environ, GIT_INDEX_FILE=idx,
                   GIT_AUTHOR_NAME="tsg", GIT_AUTHOR_EMAIL="tsg@local",
                   GIT_COMMITTER_NAME="tsg", GIT_COMMITTER_EMAIL="tsg@local")
        # only the new file, nothing else -> exactly the ceebc703 shape
        with open(os.path.join(repo, "only.txt"), "w", encoding="utf-8") as f:
            f.write("only\n")
        subprocess.run(["git", "-C", repo, "hash-object", "-w", "only.txt"],
                       capture_output=True, text=True, env=env)
        blob = _g(repo, "hash-object", "-w", "only.txt")
        subprocess.run(["git", "-C", repo, "read-tree", "--empty"], env=env,
                       capture_output=True, text=True)
        subprocess.run(["git", "-C", repo, "update-index", "--add", "--cacheinfo",
                        f"100644,{blob},only.txt"], env=env, capture_output=True, text=True)
        tree = _g_env(repo, env, "write-tree")
        bad = _g_env_commit(repo, env, tree, good)
        _g(repo, "reset", "-q", "--hard", bad)

        res2 = scan(repo, commits=1)
        leg("L2 partial-index commit is caught", not res2["clean"],
            f"drop={res2['rows'][0]['drop']} files={res2['rows'][0]['files']}")
        # 6 files -> 1 file, so the drop is 5: the surviving new file is not lost.
        leg("L3 the drop equals parent_files - files", res2["shrinks"][0]["drop"] == 5,
            f"drop={res2['shrinks'][0]['drop']} parent={res2['shrinks'][0]['parent_files']}")

        # L4: the budget lets an intentional bulk deletion through.
        res3 = scan(repo, commits=1, max_drop=10)
        leg("L4 an explicit budget clears smaller deletions", res3["clean"],
            f"max_drop=10 drop={res3['rows'][0]['drop']}")

        # L5: a root commit has no parent and must not be reported as a shrink.
        root = _g(repo, "rev-list", "--max-parents=0", "HEAD").split()[-1]
        res4 = scan(repo, commits=100, rev=root)
        row = [r for r in res4["rows"] if r["commit"] == root[:12]][0]
        leg("L5 root commit is not a shrink", row.get("root") is True and row["drop"] == 0,
            f"files={row['files']}")

        # L6: unreadable rev is a mechanism failure (rc2), not a fake pass.
        try:
            scan(repo, commits=1, rev="no-such-ref")
            ok = False
        except RuntimeError:
            ok = True
        leg("L6 unknown rev raises instead of passing", ok)

        # L7: a repaired shrink is recorded but is not a live failure -- the tip
        # already carries the files again, so this must not stay red forever.
        # Repair shape = the real one (r1133): a forward commit whose tree is the
        # good tree again, parented on the bad commit.
        idx2 = os.path.join(tmp, "repair.index")
        env2 = dict(env, GIT_INDEX_FILE=idx2)
        subprocess.run(["git", "-C", repo, "read-tree", good], env=env2,
                       capture_output=True, text=True)
        tree2 = _g_env(repo, env2, "write-tree")
        repair = _g_env_commit(repo, env2, tree2, bad)
        _g(repo, "reset", "-q", "--hard", repair)
        res5 = scan(repo, commits=5)
        leg("L7 repaired shrink is history, not a live defect",
            res5["clean"] and len(res5["shrinks"]) == 1
            and res5["shrinks"][0]["repaired"] is True,
            f"clean={res5['clean']} hits={len(res5['shrinks'])} tip={res5['tip_files']}")
    except Exception as e:  # fixture failure is a real failure
        leg("fixture", False, str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = sum(1 for _, ok, _ in legs if ok)
    print(f"\nselftest: {n_pass}/{len(legs)} PASS")
    return 0 if n_pass == len(legs) else 1


def _g_env(repo: str, env: dict, *args: str) -> str:
    p = subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr}")
    return p.stdout.strip()


def _g_env_commit(repo: str, env: dict, tree: str, parent: str) -> str:
    p = subprocess.run(["git", "-C", repo, "commit-tree", tree, "-p", parent, "-m",
                        "partial index commit"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="scan a repo's recent commits for tree shrink")
    c.add_argument("--repo", default=".", help="repo path (default: cwd)")
    c.add_argument("--commits", type=int, default=DEFAULT_COMMITS)
    c.add_argument("--max-drop", type=int, default=DEFAULT_MAX_DROP,
                   help="files a commit may delete before it is flagged (default 0)")
    c.add_argument("--rev", default="HEAD", help="tip to walk back from (default HEAD)")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_check)
    g = sub.add_parser("check_group", help="scan the group repo's origin/main tip")
    g.add_argument("--repo", default=None, help="group repo path (default: auto-detect)")
    g.add_argument("--commits", type=int, default=8)
    g.add_argument("--max-drop", type=int, default=DEFAULT_MAX_DROP)
    g.set_defaults(func=cmd_check_group)
    s = sub.add_parser("selftest", help="offline fixture tests")
    s.set_defaults(func=lambda a: cmd_selftest())
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
