# -*- coding: utf-8 -*-
"""r807(2nd) bm-c push + delivery self-verify (r805 netpath配方: HTTPS
ls-remote delivery face; r896-adjacent law: push once, fetch, ls-tree
self-verify). Fallback on rejection: ONE merge retry, then machine branch
(machine/bm-c-r807) with disclosure."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
URL = "https://github.com/BigRain-11122/BigMoney.git"


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
    rc, out, err = git(["push", "origin", "main"])
    print("PUSH rc=%d %s" % (rc, (err or out).strip()[-300:]))
    if rc != 0:
        print("push refused -- fetch + retry face")
        rc2, out2, err2 = git(["fetch", "origin"])
        print("fetch rc=%d" % rc2)
        rc3, out3, err3 = git(["push", "origin", "main"])
        print("PUSH-2 rc=%d %s" % (rc3, (err3 or out3).strip()[-300:]))
        if rc3 != 0:
            rc4, out4, err4 = git(["push", "origin",
                                   "HEAD:refs/heads/machine/bm-c-r807"])
            print("MACHINE-BRANCH rc=%d %s"
                  % (rc4, (err4 or out4).strip()[-300:]))
    rc, out, _ = git(["rev-parse", "HEAD"])
    head = out.strip()
    p = subprocess.run(["git", "ls-remote", URL, "refs/heads/main"],
                       capture_output=True, creationflags=CREATE)
    tip = (p.stdout or b"").decode("utf-8", "replace").strip().split("\t")[0]
    print("HEAD=%s remote-tip=%s delivered=%s"
          % (head[:9], tip[:9], tip == head))


if __name__ == "__main__":
    raise SystemExit(main())
