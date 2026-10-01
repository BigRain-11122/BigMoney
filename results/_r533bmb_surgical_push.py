"""r533 bm-b generic surgical reparent push (r530/r532/r534/r541 law family).

Usage: python results/_r533bmb_surgical_push.py "<commit message>" <path> [<path>...]
Diff-based payload staging onto origin/main (read-tree + per-file hash-object),
payload/deletion assertions (r530), commit-tree -p origin/main, push FF, delivery
ls-tree self-proof. Never reuses local commit tree (r530 stale-tree law).
"""
import os
import subprocess
import sys


def git(*args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(["git", *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"GIT FAIL {r.returncode}: git {' '.join(args)}\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()


def main():
    if len(sys.argv) < 3:
        print("usage: surgical_push.py <msg> <path>...")
        sys.exit(2)
    msg, payload = sys.argv[1], sys.argv[2:]
    origin = git("rev-parse", "origin/main")
    idx = os.path.abspath(".git/_surgical_idx_r533c")
    if os.path.exists(idx):
        os.remove(idx)
    env_extra = {"GIT_INDEX_FILE": idx}
    git("read-tree", origin, env_extra=env_extra)
    for p in payload:
        sha = git("hash-object", "-w", "--", p)
        git("update-index", "--add", "--cacheinfo", f"100644,{sha},{p}",
            env_extra=env_extra)
    diff = git("diff-index", "--cached", "--name-status", origin, env_extra=env_extra)
    lines = [l for l in diff.splitlines() if l.strip()]
    dels = [l for l in lines if l.startswith("D")]
    staged_paths = {l.split("\t")[-1] for l in lines}
    print(f"assert: diff={len(lines)} dels={len(dels)} payload={len(payload)}")
    if dels:
        print("ASSERT FAIL: deletion set non-empty (r519 family guard)")
        sys.exit(1)
    extra = staged_paths - set(payload)
    if extra:
        print(f"ASSERT FAIL: unexpected staged paths {extra}")
        sys.exit(1)
    tree = git("write-tree", env_extra=env_extra)
    commit = git("commit-tree", tree, "-p", origin, "-m", msg)
    git("update-ref", "refs/heads/main", commit)
    git("reset", "--mixed", commit)
    git("push", "origin", "main")
    git("fetch", "origin")
    miss = [p for p in payload if not git("ls-tree", "origin/main", "--", p).strip()]
    ahead = git("rev-list", "--count", "origin/main..HEAD")
    print(f"delivered={commit} parent={origin} missing={miss} ahead={ahead}")
    if miss or ahead != "0":
        sys.exit(1)


if __name__ == "__main__":
    main()
