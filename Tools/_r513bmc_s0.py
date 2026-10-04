"""r513 bm-c S0: zero-window git channel probe.
fetch group tree + bigmoney origin; report dirty/behind/ahead + dual
watermark blob hashes (orders SHA-1 / decisions SHA-256). No mutations:
pure probe to select integration path (merge-mode per r511 canon).
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
    rc, out, err = git(["fetch", "origin"], GROUP)
    print("GROUP-FETCH rc=%d %s" % (rc, (err or out).strip()[:120]))
    rc, out, err = git(["fetch", "origin"], ROOT)
    print("BM-FETCH rc=%d %s" % (rc, (err or out).strip()[:120]))
    rc, head, _ = git(["rev-parse", "HEAD"], ROOT)
    print("HEAD %s" % head.strip())
    rc, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"], ROOT)
    print("LOCAL-AHEAD %s" % (ahead.strip() if rc == 0 else "?"))
    rc, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"], ROOT)
    print("LOCAL-BEHIND %s" % (behind.strip() if rc == 0 else "?"))
    rc, subj, _ = git(["log", "--oneline", "-8", "HEAD..origin/main"], ROOT)
    print("--- behind commits ---")
    print(subj.strip() or "(none)")
    # dirty intersection with incoming commits (decides churn-absorb need)
    rc, st, _ = git(["status", "--porcelain"], ROOT)
    dirty = [l for l in st.splitlines() if l.strip()]
    print("DIRTY-COUNT %d" % len(dirty))
    for l in dirty[:20]:
        print(l)
    if rc == 0 and behind.strip().isdigit() and int(behind) > 0:
        rc, files, _ = git(["diff", "--name-only", "HEAD", "origin/main"], ROOT)
        incoming = set((files or "").splitlines())
        inter = [d[3:].strip() for d in dirty if d[3:].strip() in incoming]
        print("DIRTY-INTERSECT-INCOMING %d %s" % (len(inter), inter[:10]))
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
