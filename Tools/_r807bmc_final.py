# -*- coding: utf-8 -*-
"""r807(2nd) bm-c final bookkeeping commit + push (round closeout face)."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "_r807bmc_finalmsg.txt")


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
    n = len([l for l in out.splitlines() if l.strip()])
    print("dirty_n=%d" % n)
    if n == 0:
        print("nothing to commit")
        return 0
    with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("round 807: half-open rebase takeover closeout (6/6 picks + "
                 "T2 product preserved, merge 12-face zero-loss, push "
                 "delivery-verified) + close bookkeeping + smoke 49/49 "
                 "[via bm-c r807]\n")
    rc, out, err = git(["add", "-A"])
    print("add rc=%d" % rc)
    rc, out, err = git(["commit", "-F", MSG])
    print("commit rc=%d %s" % (rc, (err or out).strip()[:200]))
    rc, out, err = git(["push", "origin", "main"])
    print("push rc=%d %s" % (rc, (err or out).strip()[-200:]))
    if rc != 0:
        rc2, _, _ = git(["fetch", "origin"])
        rc3, out3, err3 = git(["push", "origin", "main"])
        print("push-2 rc=%d %s" % (rc3, (err3 or out3).strip()[-200:]))
        if rc3 != 0:
            rc4, out4, err4 = git(["push", "origin",
                                   "HEAD:refs/heads/machine/bm-c-r807"])
            print("machine-branch rc=%d %s" % (rc4, (err4 or out4).strip()[-150:]))
    rc, out, _ = git(["rev-parse", "HEAD"])
    head = out.strip()
    p = subprocess.run(["git", "ls-remote",
                        "https://github.com/BigRain-11122/BigMoney.git",
                        "refs/heads/main"], capture_output=True,
                       creationflags=CREATE)
    tip = (p.stdout or b"").decode("utf-8", "replace").strip().split("\t")[0]
    print("HEAD=%s tip=%s delivered=%s" % (head[:9], tip[:9], tip == head))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
