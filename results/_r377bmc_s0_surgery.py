# -*- coding: utf-8 -*-
"""r377 bm-c S0 surgical realign (r578 law).

Local HEAD f3cdd9031 (r376 wrap) -> origin/main fe191d370 (bm-a r586 W104 union
+ bm-b r585 W100 finalize/W103 tail/W106 seat). Dirty live-writer tree forbids
rebase (r532 law) -> reset --mixed + selective checkout:
  - KEEP local: 4 bm-c live-writer faces (W105 tail products + telemetry)
  - TAKE origin: every M/D face in the delta (law table, N1 scripts, W103
    shards 8-11, W100 finalize product, W106 seat MSG, bm-b receipts)
  - DELETE: old-path inbox seat MSG copies superseded by processed/ R100 moves
  - KEEP untracked: results/_r376bmc_wrap.py (r376 residue, wrap payload rides)
Post-verify: status set == KEEP-4 + wrap residue, else exit 2.
"""
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NW = 0x08000000  # CREATE_NO_WINDOW (U060 zero-flash law)


def git(*a, check=True):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, creationflags=NW)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if check and r.returncode != 0:
        print("GITFAIL", list(a)[:3], err[:300])
        sys.exit(1)
    return r.returncode, out, err


KEEP = {
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
}
OLD_MSG = [
    "fleet/inbox/MSG-20261002-1712-bma-w104-seat.md",
    "fleet/inbox/MSG-20261002-1738-bmc-w105-seat.md",
]
UNTRACKED_KEEP = {"results/_r376bmc_wrap.py"}


def main():
    rc, out, _ = git("rev-parse", "HEAD")
    head0 = out.strip()
    rc, out, _ = git("rev-parse", "origin/main")
    om = out.strip()
    if head0 == om:
        print("ALREADY_ALIGNED", om)
        return
    print("realign", head0[:9], "->", om[:9])

    git("reset", "--mixed", "origin/main")
    rc, out, _ = git("status", "--porcelain")
    lines = [l for l in out.splitlines() if l.strip()]
    checkout, untracked, kept = [], [], []
    for l in lines:
        st, path = l[:2], l[3:].strip().strip('"')
        if st == "??":
            untracked.append(path)
            continue
        if path in KEEP:
            kept.append((st, path))
            continue
        checkout.append(path)
    print("checkout N =", len(checkout), "| untracked:", untracked,
          "| kept-live-writers:", [k[1] for k in kept])
    if checkout:
        git("checkout", "--", *checkout)
    deleted = []
    for p in OLD_MSG:
        fp = os.path.join(REPO, *p.split("/"))
        if os.path.exists(fp):
            os.remove(fp)
            deleted.append(p)
    rc, out, _ = git("status", "--porcelain")
    print("post-status:")
    print(out)
    allowed = KEEP | UNTRACKED_KEEP
    bad = []
    for l in out.splitlines():
        if not l.strip():
            continue
        path = l[3:].strip().strip('"')
        if path not in allowed:
            bad.append((l[:2], path))
    if bad:
        print("SURGERY_VERIFY_FAIL", bad)
        sys.exit(2)
    print("SURGERY_OK | deleted-old-msg:", deleted)
    rc, out, _ = git("rev-parse", "HEAD")
    print("HEAD now", out.strip()[:9])


if __name__ == "__main__":
    main()
