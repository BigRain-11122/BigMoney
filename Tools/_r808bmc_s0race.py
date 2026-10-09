# -*- coding: utf-8 -*-
"""r808 bm-c S0 race closeout: absorb-loop add->commit->pull --rebase up to 3x
(daemon live-face rewrite race; net-tree zero-autostash law r642 held)."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "_r_bmc_s0msg.txt")


def git(args, timeout=75):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           creationflags=CREATE, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "leg timeout"


def main():
    for attempt in (1, 2, 3):
        rc, st, _ = git(["status", "--porcelain"])
        dirty = [l for l in st.splitlines() if l.strip()]
        if not dirty:
            print("attempt %d: tree already clean" % attempt)
            rc, out, err = git(["pull", "--rebase", "origin", "main"])
            print("PULL rc=%d %s" % (rc, (err or out).strip()[-300:]))
            if rc == 0:
                rc2, cnt, _ = git(["rev-list", "--left-right", "--count",
                                   "HEAD...origin/main"])
                print("AHEAD-BEHIND %s" % cnt.strip())
                return 0
            continue
        paths = [l[3:].strip().strip('"') for l in dirty]
        rc, out, err = git(["add", "--"] + paths)
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 808 S0: absorb daemon live faces retry%d (%d files)\n"
                    % (attempt, len(paths)))
        rc, out, err = git(["commit", "-F", MSG])
        rc2, head, _ = git(["rev-parse", "--short", "HEAD"])
        print("attempt %d: ABSORB %s" % (attempt, head.strip()))
        rc, out, err = git(["pull", "--rebase", "origin", "main"])
        print("PULL rc=%d %s" % (rc, (err or out).strip()[-300:]))
        if rc == 0:
            rc2, cnt, _ = git(["rev-list", "--left-right", "--count",
                               "HEAD...origin/main"])
            print("AHEAD-BEHIND %s" % cnt.strip())
            return 0
    print("RACE-UNRESOLVED after 3 attempts (report + read-only fallback)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
