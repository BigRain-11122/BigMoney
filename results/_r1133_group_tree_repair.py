"""r1133 P0 repair: group origin/main tip ceebc703 carries a tree with only 2
files (3,494 deleted) because its closeout built the commit from a partial
index. Repair = new commit whose tree is the previous good tree (e76739bb) PLUS
the two receipts the bad commit genuinely added. Pure plumbing: no worktree
touch, no history rewrite, parent = the bad commit (plain fast-forward push).
"""
import os
import subprocess
import sys
import tempfile

GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
BAD = "ceebc703e1b239d3e1382340736919faf9d8c7bf"   # tree-wiped tip
GOOD = "e76739bb"                                    # previous good tip
NEW = [
    "cph4/fleet/order-bus/receipts/OB-20261027-202256-910-bm-b.json",
    "cph4/fleet/order-bus/receipts/OB-20261027-211206-860-bm-b.json",
]


def git(*args, **kw):
    env = dict(os.environ, **kw.pop("env", {}))
    p = subprocess.run(["git"] + list(args), cwd=GROUP, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        raise SystemExit(f"git {args[0]} failed rc={p.returncode}: {p.stdout}\n{p.stderr}")
    return p.stdout.strip()


def main():
    git("fetch", "origin")
    tip = git("rev-parse", "origin/main")
    if not tip.startswith(BAD[:12]):
        print(f"ABORT: origin/main moved to {tip} -- owner is active, not touching it")
        return 1
    good = git("rev-parse", GOOD)
    print(f"baseline good tree = {good}  bad tip = {tip[:12]}")

    idx = os.path.join(tempfile.gettempdir(), "r1133_group_repair.index")
    if os.path.exists(idx):
        os.remove(idx)
    env = {"GIT_INDEX_FILE": idx}
    git("read-tree", good, env=env)
    n_before = len(git("ls-tree", "-r", "--name-only", good).splitlines())

    for path in NEW:
        blob = git("rev-parse", f"{BAD}:{path}")
        git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        print(f"  + {path} blob {blob[:10]}")

    tree = git("write-tree", env=env)
    n_after = len(git("ls-tree", "-r", "--name-only", tree).splitlines())
    print(f"tree {tree[:12]} files={n_after} (baseline {n_before}, delta {n_after - n_before})")
    if n_after < n_before:
        print("ABORT: repair tree lost files")
        return 2

    msg = ("P0 REPAIR: restore the group tree deleted by ceebc703\n\n"
           "ceebc703 was built from a partial index, so its tree carried only the two\n"
           "receipts it meant to add and dropped all 3,494 other files (docs/decisions.md,\n"
           "docs/orders.md, cph4/, fleet docs -- the whole group face).\n\n"
           "This commit is a plain forward commit on top of ceebc703 whose tree is the\n"
           "previous good tree (e76739bb) plus exactly those two receipt blobs, so nothing\n"
           "is rewritten and the receipts survive. Repaired by bm-a r1133 (found via the\n"
           "D-19 watermark probe reading decisions.md as unreachable).\n\n"
           "Root cause to fix at the writer: a surgical closeout must seed its temp index\n"
           "from the parent tree (read-tree) and assert the resulting file count, never\n"
           "write-tree from an empty/partial index.\n")
    commit = git("commit-tree", tree, "-p", tip, "-m", msg)
    print(f"commit {commit}")

    git("push", "origin", f"{commit}:refs/heads/main")
    git("fetch", "origin")
    new_tip = git("rev-parse", "origin/main")
    n_tip = len(git("ls-tree", "-r", "--name-only", new_tip).splitlines())
    print(f"PUSH-OK origin/main={new_tip[:12]} files={n_tip}")
    print("decisions.md present:", bool(git("rev-parse", f"{new_tip}:docs/decisions.md")))
    return 0 if n_tip >= n_before else 3


if __name__ == "__main__":
    sys.exit(main())