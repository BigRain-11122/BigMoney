"""r533 bm-b restoration payload reparent push (origin moved mid-window).

r530/r532 surgical route: read-tree origin/main + stage ONLY the 4 restored
payload files (diff-based payload staging -- never reuse local commit tree,
r530 law); payload/deletion assertions; commit-tree -p origin/main; push FF.
"""
import os
import subprocess
import sys

PAYLOAD = [
    "fleet/inbox/MSG-20261002-021x-bm-a.md",
    "fleet/inbox/MSG-20261002-025x-bm-c-nulls-yield.md",
    "results/_r344bmc_closeout.py",
    "results/lowamp_p3/sens.jsonl",
]
MSG = ("r533 restore: byte-checkout recovery of 4 files deleted by bm-b autofill "
       "tick keepalive 6765a3b93 (reset--mixed lag-window x daemon full-sweep, "
       "new r519-family variant; r540 hold-commit fc7cbf365 recovery zero "
       "re-derive): lowamp_p3/sens.jsonl 500/500 P3-finalize blocker + "
       "_r344bmc_closeout.py bm-c tool + 2 unprocessed inbox MSGs [via bm-b]")


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
    origin = git("rev-parse", "origin/main")
    idx = os.path.abspath(".git/_surgical_idx_r533b")
    if os.path.exists(idx):
        os.remove(idx)
    env_extra = {"GIT_INDEX_FILE": idx}
    git("read-tree", origin, env_extra=env_extra)
    for p in PAYLOAD:
        sha = git("hash-object", "-w", "--", p)
        git("update-index", "--add", "--cacheinfo", f"100644,{sha},{p}",
            env_extra=env_extra)
    diff = git("diff-index", "--cached", "--name-status", origin, env_extra=env_extra)
    lines = [l for l in diff.splitlines() if l.strip()]
    dels = [l for l in lines if l.startswith("D")]
    print(f"assert: diff={len(lines)} dels={len(dels)} lines={lines}")
    if dels or len(lines) != len(PAYLOAD):
        print("ASSERT FAIL: payload shape violated (expect exactly 4 A/M, 0 D)")
        sys.exit(1)
    for l in lines:
        path = l.split("\t")[-1]
        if path not in PAYLOAD:
            print(f"ASSERT FAIL: unexpected path {path}")
            sys.exit(1)
    tree = git("write-tree", env_extra=env_extra)
    commit = git("commit-tree", tree, "-p", origin, "-m", MSG)
    git("update-ref", "refs/heads/main", commit)
    git("reset", "--mixed", commit)
    git("push", "origin", "main")
    git("fetch", "origin")
    miss = [p for p in PAYLOAD if not git("ls-tree", "origin/main", "--", p).strip()]
    ahead = git("rev-list", "--count", "origin/main..HEAD")
    print(f"delivered commit={commit} parent={origin} missing={miss} ahead={ahead}")


if __name__ == "__main__":
    main()
