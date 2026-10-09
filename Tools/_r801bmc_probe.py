# -*- coding: utf-8 -*-
"""r801 bm-c continuation probe: git status/branch/ahead-behind/log after
prior-session crash (rebase resolved 11:59, S6/QA done 12:02, no closing commit).
Zero-window: subprocess CREATE_NO_WINDOW (r801 law).
"""
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


rc, out, err = git(["status", "--porcelain=v1"])
print("== status porcelain ==")
print(out if out.strip() else "(clean)")
print("rc=%d" % rc)

rc, out, err = git(["log", "--oneline", "-8"])
print("== log -8 ==")
print(out)

rc, out, err = git(["rev-list", "--left-right", "--count", "main...origin/main"])
print("== ahead/behind main vs origin/main (ahead<TAB>behind) ==")
print(out)

rc, out, err = git(["status", "-sb"])
print("== status -sb ==")
print(out)
