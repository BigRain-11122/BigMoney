"""r1001 successor S0 absorption (dead-window estate, takeover per r899 precedent).

Prior r1001 window died ~21:43 mid W243 prereg derive (no Bigmoney codely alive at 21:48 census;
sole successor = this window). Estate handling:
- 3 treasure_guard FORBIDDEN faces (append-only/registry) + quarantine manifest: committed
  BEFORE rebase = zero loss of appended rows (attrition guard superset law).
- 33 regenerable faces: discarded (guard rc0 restorable), S6 chain this round re-derives post-bar.
- Rebase onto origin d9b0aab9a (bm-c r1009, 1 commit behind). bm-c commit does not touch the
  3 preserved files -> zero-conflict replay expected.
"""
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PRESERVE = [
    "results/pool_dualrun.bm-a.jsonl",
    "results/prospect_promotion/_summary.json",
    "results/token_usage.bm-a.json",
    "results/_quarantine/manifest.json",
    "results/_quarantine/20261014-2125_r1001bma_prebar_faces/",
]
DIRTY_LIST = r"_r1001bma_dirty_paths.txt"


def run(args, **kw):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", **kw)
    return p.returncode, p.stdout, p.stderr


def main():
    # 1) commit preserved faces (estate absorption)
    rc, out, err = run(["git", "add"] + PRESERVE)
    print("add preserve rc", rc, err.strip()[:200])
    rc, out, err = run(["git", "commit", "-m",
                        "r1001 pre-absorb estate: preserve append-only ledgers + registry + "
                        "quarantine manifest from dead prior window (guard rc3 faces; "
                        "33 regenerable faces discarded pre-rebase, chain re-derives post-bar)"])
    print("commit preserve rc", rc, (out + err).strip()[:300])
    if rc != 0:
        print("ABORT: preserve commit failed")
        sys.exit(1)
    # 2) discard the rest of dirty tracked faces (guard already rc0-restorable for all listed)
    with open(DIRTY_LIST, encoding="ascii") as f:
        paths = [ln.strip() for ln in f if ln.strip()]
    discard = [p for p in paths if p not in PRESERVE]
    if discard:
        rc, out, err = run(["git", "checkout", "--"] + discard)
        print("discard %d faces rc" % len(discard), rc, err.strip()[:200])
        if rc != 0:
            print("ABORT: discard failed")
            sys.exit(1)
    # 3) rebase onto origin
    rc, out, err = run(["git", "pull", "--rebase", "origin", "main"])
    print("pull --rebase rc", rc)
    print((out + err).strip()[:600])
    if rc != 0:
        print("ABORT: rebase not clean -> hand back to caller for resolver path")
        sys.exit(2)
    # 4) verify
    rc, out, _ = run(["git", "rev-list", "--count", "HEAD..origin/main"])
    print("behind:", out.strip())
    rc, out, _ = run(["git", "status", "--porcelain"])
    dirty = [ln for ln in out.splitlines() if ln.strip()]
    print("dirty after:", len(dirty))
    for ln in dirty[:10]:
        print("  ", ln[:120])
    print("OK")


if __name__ == "__main__":
    main()
