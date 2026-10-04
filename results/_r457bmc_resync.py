"""r457 bm-c resync: fetch + pull --rebase (absorb commit replays), then identity re-probe."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git(["status", "--porcelain"])
    dirty = [l for l in out.splitlines() if l.strip() and not l.strip().startswith("??")]
    print("DIRTY (tracked, pre-rebase): %d" % len(dirty))
    for l in dirty[:12]:
        print("  ", l)
    rc, out, err = git(["pull", "--rebase"])
    print("PULL-REBASE rc=%d" % rc)
    tail = (out + err).strip().splitlines()
    print("\n".join(tail[-6:]) if tail else "(clean)")
    rb = os.path.join(ROOT, ".git", "rebase-merge")
    print("REBASE-MERGE-EXIST %s" % os.path.exists(rb))
    rc, a, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    rc2, b, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    print("AHEAD %s BEHIND %s" % (a.strip(), b.strip()))
    rc, lg, _ = git(["log", "--oneline", "-3", "origin/main"])
    print("--- origin tip ---")
    print(lg.strip())


if __name__ == "__main__":
    main()
