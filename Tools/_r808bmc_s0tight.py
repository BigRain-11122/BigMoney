# -*- coding: utf-8 -*-
"""r808 bm-c S0 tight-window closeout: single-shot add->commit->pull inside the
daemon write gap; on refusal, print the exact blocking status."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000


def git(args, timeout=60):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, st, _ = git(["status", "--porcelain"])
    dirty = [l[3:].strip().strip('"') for l in st.splitlines() if l.strip()]
    print("PRE-DIRTY %d: %s" % (len(dirty), dirty))
    if dirty:
        git(["add", "--"] + dirty)
        rc, out, err = git(["commit", "-m",
                            "round 808 S0: tight-window absorb (%d faces)" % len(dirty)])
        print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:150]))
    rc, st, _ = git(["status", "--porcelain"])
    print("POSTCOMMIT-DIRTY: %s" % ([l for l in st.splitlines() if l.strip()],))
    rc, out, err = git(["pull", "--rebase", "origin", "main"])
    print("PULL rc=%d %s" % (rc, (err or out).strip()[-300:]))
    if rc != 0:
        rc2, st2, _ = git(["status", "--porcelain"])
        print("BLOCKERS: %s" % ([l for l in st2.splitlines() if l.strip()],))
    else:
        rc3, cnt, _ = git(["rev-list", "--left-right", "--count",
                            "HEAD...origin/main"])
        print("AHEAD-BEHIND %s" % cnt.strip())
        rc4, h, _ = git(["rev-parse", "--short", "HEAD"])
        print("HEAD %s" % h.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
