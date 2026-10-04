"""r504 bm-c S0: zero-window git channel (U060/O-67fbec7 flash-guard family).
fetch group tree first (D-19 fresh-read law) + bigmoney pull --rebase +
porcelain status + dual watermark blob hashes (orders SHA-1 / decisions
SHA-256). All git children CREATE_NO_WINDOW."""
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
    rc, out, err = git(["fetch", "origin"], GROUP)
    print("GROUP-FETCH rc=%d %s" % (rc, (err or out).strip()[:120]))
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
