# -*- coding: utf-8 -*-
"""r536 bm-c push-race recovery: fetch, behind census, incoming files, UU list.
Pure probe first (r524 law: behind>0 -> integrate then push, zero exceptions)."""
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


rc, out, err = git(["fetch", "origin"])
print("FETCH rc=%d" % rc)
rc, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
rc, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
print("AHEAD %s BEHIND %s" % (ahead.strip(), behind.strip()))
rc, subj, _ = git(["log", "--oneline", "-10", "HEAD..origin/main"])
print("--- incoming ---")
print(subj.strip())
rc, files, _ = git(["diff", "--name-only", "HEAD", "origin/main"])
print("--- incoming files ---")
print(files.strip())
