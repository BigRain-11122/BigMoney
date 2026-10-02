# -*- coding: utf-8 -*-
"""r377 bm-c: surgical re-parent of the product payload onto the fresh origin tip.

Context: my product commit 286058137 (parent fe191d370) was push-rejected
non-ff because bm-b landed the W106 FREEZE (d6b2952e3) inside my window.
r523 law: rebuild the payload on the new origin base instead of bypassing.

Steps:
  1. sanity: HEAD must be my product commit, origin must have moved past it
  2. git reset --mixed origin/main  (keep working tree)
  3. classify status:
       MINE (M)  = 4 telemetry faces        -> stage fresh content
       MINE (??) = 3 receipts + processed MSG copy -> stage
       MSG-MOVE  = worktree-deleted inbox seat MSG (mine) -> stage deletion
       OTHER (M) = bm-b W106-freeze faces stale in worktree -> checkout origin
  4. commit -F msg, push, fetch, ls-tree delivery verify
"""
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\msg-r377c-product2.txt"
NW = 0x08000000  # CREATE_NO_WINDOW (U060 zero-flash law)

MY_M = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
MY_NEW = [
    "results/_r376bmc_wrap.py",
    "results/_r377bmc_s0_surgery.py",
    "results/_r377bmc_probe_w100.py",
]
MSG_INBOX = "fleet/inbox/MSG-20261002-1733-bmb-w106-seat.md"
MSG_PROC = "fleet/inbox/processed/MSG-20261002-1733-bmb-w106-seat.md"


def git(*a, check=True):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, creationflags=NW)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if check and r.returncode != 0:
        print("GITFAIL", list(a)[:3], err[:300])
        sys.exit(1)
    return r.returncode, out, err


def main():
    rc, out, _ = git("rev-parse", "HEAD")
    head = out.strip()
    rc, out, _ = git("rev-parse", "origin/main")
    om = out.strip()
    if head == om:
        print("ALREADY_DELIVERED", om[:9])
        sys.exit(0)
    # sanity: HEAD must be my unpushed product commit (parent = old origin base)
    rc, out, _ = git("rev-parse", "HEAD~1")
    parent = out.strip()
    rc_code = subprocess.run(
        ["git", "merge-base", "--is-ancestor", parent, om], cwd=REPO,
        capture_output=True, creationflags=NW).returncode
    if rc_code != 0:
        print("UNEXPECTED: my commit's parent is not an ancestor of origin",
              parent[:9], om[:9])
        sys.exit(2)
    print("reparent base", head[:9], "onto", om[:9])

    git("reset", "--mixed", om)
    rc, out, _ = git("status", "--porcelain")
    checkout, add_m, add_new, stage_del, untracked = [], [], [], [], []
    for l in out.splitlines():
        if not l.strip():
            continue
        st, path = l[:2], l[3:].strip().strip('"')
        if st == "??":
            untracked.append(path)
            continue
        if path in MY_M:
            add_m.append(path)
        elif path == MSG_INBOX and "D" in st:
            stage_del.append(path)  # my move: stage the deletion
        else:
            checkout.append(path)   # bm-b W106 faces stale in worktree -> origin
    print("checkout(origin):", checkout)
    print("stage-mine:", add_m, "| stage-del:", stage_del, "| untracked:", untracked)
    for p in MY_NEW:
        if p not in untracked:
            print("MISSING RECEIPT (already tracked?):", p)
    if checkout:
        git("checkout", "--", *checkout)
    if add_m:
        git("add", "--", *add_m)
    new_here = [p for p in MY_NEW if p in untracked]
    proc_here = [p for p in untracked if p == MSG_PROC]
    if stage_del:
        git("add", "--", *stage_del)
    if new_here or proc_here:
        git("add", "--", *(new_here + proc_here))
    rc, out, _ = git("diff", "--cached", "--stat")
    print("staged:\n", out)
    rc, out, err = git("commit", "-F", MSG, check=False)
    print("commit rc", rc, (out or err)[:200])
    if rc != 0:
        sys.exit(3)
    rc, out, err = git("push", "origin", "main", check=False)
    print("push rc", rc, (out or err)[:300])
    if rc != 0:
        print("PUSH BLOCKED AGAIN -- rerun this script after next fetch")
        sys.exit(4)
    git("fetch", "origin")
    rc, out, _ = git("rev-parse", "HEAD")
    head2 = out.strip()
    rc, out, _ = git("ls-tree", "origin/main", "results/saturation_engine/face_bm-c.json")
    print("origin face row:", out.strip())
    rc, out, _ = git("ls-tree", "HEAD", "results/saturation_engine/face_bm-c.json")
    print("local  face row:", out.strip())
    rc, out, _ = git("log", "--oneline", "-n", "2", "origin/main")
    print("origin tip:", out.strip()[:120])
    print("REPARENT_DELIVERED", head2[:9])


if __name__ == "__main__":
    main()
