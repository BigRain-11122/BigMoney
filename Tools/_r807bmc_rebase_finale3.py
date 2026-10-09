# -*- coding: utf-8 -*-
"""r807(2nd) bm-c rebase finale v3: post-quit state recovery.
quit reset the index; pick-6 (s0-tail2 engine live-face absorb) content
lives on in the worktree (daemon live faces = live-wins superset + my
round scripts/receipts). Commit it with the ORIGINAL pick-6 message+author
(recovered from commit object), then branch -f main + checkout main.
After: merge origin/main (Phase B handled by separate driver)."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
PICK6 = "a0c2b3e8783fe8bbd3f3ec3b18e0c28485ba290c"
MSG = os.path.join(ROOT, "_r807bmc_pick6msg.txt")


def git(args, env=None):
    e = dict(os.environ)
    e["PYTHONUTF8"] = "1"
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE, env=e)
    return (p.returncode, (p.stdout or b"").decode("utf-8", "replace"),
            (p.stderr or b"").decode("utf-8", "replace"))


def main():
    rc, out, _ = git(["status", "--porcelain"])
    print("dirty before add:")
    for l in out.splitlines():
        if l.strip():
            print("  " + l)
    rc, out, err = git(["log", "-1", "--format=%an%n%ae%n%aI%n%B", PICK6])
    an, ae, ad, msg = out.split("\n", 3)
    with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(msg if msg.endswith("\n") else msg + "\n")
    rc1, o1, e1 = git(["add", "-A"])
    rc2, o2, e2 = git(["commit", "-F", MSG],
                      env={"GIT_AUTHOR_NAME": an, "GIT_AUTHOR_EMAIL": ae,
                           "GIT_AUTHOR_DATE": ad})
    print("add rc=%d commit rc=%d %s" % (rc1, rc2, (e2 or o2).strip()[:250]))
    if rc2 != 0:
        return 2
    rc, out, _ = git(["rev-parse", "HEAD"])
    head = out.strip()
    rc, out, err = git(["branch", "-f", "main", head])
    print("branch -f main rc=%d" % rc)
    rc, out, err = git(["checkout", "main"])
    print("checkout rc=%d %s" % (rc, (err or out).strip()[:150]))
    rc, out, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    print("ahead_behind: %s" % out.strip())
    rc, out, _ = git(["log", "--oneline", "-9"])
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
