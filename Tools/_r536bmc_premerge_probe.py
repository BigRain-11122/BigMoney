# -*- coding: utf-8 -*-
"""r536 bm-c pre-merge probe: dirty faces x incoming-file intersection
(would-be-overwritten gate, r523-1/r620 law)."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


rc, out, _ = git(["status", "--porcelain"])
dirty = [l[3:].strip().strip('"') for l in out.splitlines() if l.strip()]
print("DIRTY %d" % len(dirty))
for d in dirty:
    print(" ", d)
rc, files, _ = git(["diff", "--name-only", "HEAD", "origin/main"])
incoming = set(files.splitlines())
inter = [d for d in dirty if d in incoming]
print("INTERSECT-INCOMING %d %s" % (len(inter), inter))
