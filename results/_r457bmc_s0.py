"""r457 bm-c S0: zero-window git channel (U060 flash-guard family; r452 group-fetch-in-probe law).
rebase-leftover check (r630 law) + fetch/pull --rebase + porcelain + ahead/behind
+ D-19 raw-blob sha256 (decisions) / sha1 (group orders) + reflog near-window probe.
All git children CREATE_NO_WINDOW."""
import hashlib
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))


def git(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    rb = os.path.join(ROOT, ".git", "rebase-merge")
    print("REBASE-MERGE-EXIST %s" % os.path.exists(rb))
    rc, br, _ = git(["branch", "--show-current"], ROOT)
    print("BRANCH %s" % br.strip())
    rc, out, err = git(["fetch", "origin"], ROOT)
    print("FETCH rc=%d %s" % (rc, err.strip()[:120]))
    rc, out, err = git(["pull", "--rebase"], ROOT)
    print("PULL-REBASE rc=%d" % rc)
    tail = (out + err).strip().splitlines()
    print("\n".join(tail[-12:]) if tail else "(up to date, no output)")
    rc, st, _ = git(["status", "--porcelain"], ROOT)
    dirty = [l for l in st.splitlines() if l.strip()]
    print("DIRTY-COUNT %d" % len(dirty))
    for l in dirty[:30]:
        print(l)
    rc, head, _ = git(["rev-parse", "--short", "HEAD"], ROOT)
    print("HEAD %s" % head.strip())
    rc, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"], ROOT)
    print("LOCAL-AHEAD-OF-ORIGIN %s" % (ahead.strip() if rc == 0 else "?"))
    rc, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"], ROOT)
    print("LOCAL-BEHIND-ORIGIN %s" % (behind.strip() if rc == 0 else "?"))
    rc, subj, _ = git(["log", "--oneline", "-5", "HEAD..origin/main"], ROOT)
    print("--- behind commits ---")
    print(subj.strip() or "(none)")
    # r643 evidence-1: reflog near-window (non-self merge/commit timestamps)
    rc, rl, _ = git(["reflog", "-8", "--date=iso", "--pretty=%h %gd %gs @ %ad"], ROOT)
    print("--- reflog -8 ---")
    print("\n".join(rl.strip().splitlines()[-8:]))
    # group faces (fetch first per r452 law)
    rc, out, err = git(["fetch", "origin"], GROUP)
    print("GROUP-FETCH rc=%d %s" % (rc, err.strip()[:120]))
    rc, blob, err = git_raw(["show", "origin/main:docs/orders.md"], GROUP)
    if rc == 0:
        print("GROUP-ORDERS-SHA %s" % hashlib.sha1(blob).hexdigest().upper())
    else:
        print("GROUP-ORDERS-SHA UNAVAILABLE %s" % err.strip()[:160])
    rc, blob, err = git_raw(["show", "origin/main:docs/decisions.md"], GROUP)
    if rc == 0:
        print("GROUP-DECISIONS-SHA %s" % hashlib.sha256(blob).hexdigest().upper())
    else:
        print("GROUP-DECISIONS-SHA UNAVAILABLE %s" % err.strip()[:160])


if __name__ == "__main__":
    main()
