"""r376 bm-c S0 surgery: pure fast-forward realign after r375 surgical push.

Laws applied:
- r578: after CAS/surgical push, checkout main = zero-action; correct = reset
  --mixed re-anchor + per-face checkout.
- r580/r595: PS argv to git batch path ops unreliable -> python subprocess argv.
- Live-writer KEEP set: my machine's daemon-owned files stay local (they are
  rewritten every tick; checkout would fight the writers).
Everything else dirty (stale origin-aligned snapshot vs new origin) is
restored from the freshly re-anchored index == origin/main.
"""
import subprocess
import sys
import json

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW, U060 zero-flash law

# bm-c live-writer files (daemon rewrites these between commits -> keep local)
KEEP = {
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine/history_bm-c.jsonl",
    "results/saturation_engine/ledger_bm-c.jsonl",
    "results/pool_dualrun.bm-c.jsonl",
    "state-bm-c.json",
}


def git(*args, check=True):
    r = subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, creationflags=NO_WINDOW
    )
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if check and r.returncode != 0:
        print("GITFAIL", list(args), "rc=", r.returncode)
        print(err[:800])
        sys.exit(1)
    return out, err, r.returncode


def main():
    # 0) safety: confirm pure fast-forward (0 local-only commits)
    _, _, rc = git("rev-list", "--count", "origin/main..main", check=False)
    ahead = int(_ or 0) if rc == 0 else -1
    if ahead not in (0,):
        print("ABORT: local main ahead of origin by", ahead, "-- not ff, manual review")
        sys.exit(2)

    # 1) re-anchor HEAD+index to origin/main (worktree untouched)
    git("reset", "--mixed", "origin/main")

    # 2) classify dirty files (NUL-separated, robust to spaces/quotes)
    out, _, _ = git("status", "--porcelain", "-z")
    entries = []
    for rec in out.split("\0"):
        if not rec:
            continue
        st = rec[:2]
        path = rec[3:]
        entries.append((st, path))

    keep_seen, restore, untracked = [], [], []
    for st, path in entries:
        if st == "??":
            untracked.append(path)
        elif path in KEEP:
            keep_seen.append((st, path))
        else:
            restore.append(path)

    # 3) restore stale faces from re-anchored index (== origin/main)
    for i in range(0, len(restore), 200):
        batch = restore[i : i + 200]
        git("checkout", "--", *batch)

    # 4) report
    out2, _, _ = git("status", "--porcelain", "-z")
    remaining = [rec[:2] + " " + rec[3:] for rec in out2.split("\0") if rec]
    print(json.dumps({
        "kept_local": keep_seen,
        "restored_count": len(restore),
        "untracked_count": len(untracked),
        "remaining_dirty": remaining,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
