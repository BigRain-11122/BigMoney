"""r533 bm-b S0 surgical integration (r530/r532 law: tracked live-writer blocks rebase).

Diff-based payload staging: temp index from origin/main + per-file hash-object
of local dirty lane files; payload-count + deletion-set assertions (r530/r543/r343);
commit-tree -p origin/main; update-ref; reset --mixed; push FF; ls-tree delivery proof.
"""
import subprocess
import sys
import os

PAYLOAD = [
    "results/autofill_state.bm-b.json",
    "results/lowamp_p3/nulls.jsonl",
    "results/p1d_gates.json",
    "results/p2cal_ext/n1_w44/shard-1-of-12.json",
    "results/pool_core_samples.jsonl",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/ledger_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
]
MSG = ("r533 ride-1: surgical lane carry over origin fc5a5c28a "
       "(W44 bm-b shard-1 evidence + LOWAMP-P3-NULLS in-flight checkpoint + engine lane files "
       "+ pool_core_samples union origin501+bm-b1) [via bm-b]")


def git(*args, **kw):
    env = dict(os.environ)
    env.update(kw.pop("env_extra", {}))
    r = subprocess.run(["git", *args], capture_output=True, text=True, env=env, **kw)
    if r.returncode != 0:
        print(f"GIT FAIL {r.returncode}: git {' '.join(args)}\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()


def main():
    origin = git("rev-parse", "origin/main")
    idx = os.path.abspath(".git/_surgical_idx_r533")
    if os.path.exists(idx):
        os.remove(idx)
    env_extra = {"GIT_INDEX_FILE": idx}
    git("read-tree", origin, env_extra=env_extra)
    staged = 0
    for p in PAYLOAD:
        sha = git("hash-object", "-w", "--", p)
        git("update-index", "--add", "--cacheinfo", f"100644,{sha},{p}", env_extra=env_extra)
        staged += 1
    # assertions vs origin/main (r343: must be --cached)
    diff = git("diff-index", "--cached", "--name-status", origin, env_extra=env_extra)
    lines = [l for l in diff.splitlines() if l.strip()]
    statuses = [l.split("\t")[0] for l in lines]
    dels = [l for l in lines if l.startswith("D")]
    adds = [l for l in lines if l.startswith("A")]
    print(f"assert: diff lines={len(lines)} statuses={set(statuses)} dels={len(dels)} adds={len(adds)}")
    if dels:
        print("ASSERT FAIL: deletion set non-empty (r530 law)")
        sys.exit(1)
    if len(lines) > staged:
        print("ASSERT FAIL: diff wider than payload")
        sys.exit(1)
    for l in lines:
        path = l.split("\t")[-1]
        if path not in PAYLOAD:
            print(f"ASSERT FAIL: unexpected staged path {path}")
            sys.exit(1)
    tree = git("write-tree", env_extra=env_extra)
    commit = git("commit-tree", tree, "-p", origin, "-m", MSG)
    print(f"new commit {commit} parent {origin}")
    git("update-ref", "refs/heads/main", commit)
    git("reset", "--mixed", commit)
    git("push", "origin", "main")
    git("fetch", "origin")
    # delivery self-proof: ls-tree each payload path on origin/main
    miss = []
    for p in PAYLOAD:
        out = git("ls-tree", "origin/main", "--", p)
        if not out.strip():
            miss.append(p)
    print(f"delivery: missing={miss}")
    ahead = git("rev-list", "--count", "origin/main..HEAD")
    print(f"ahead_after_push={ahead} commit={commit}")
    if miss:
        sys.exit(1)


if __name__ == "__main__":
    main()
