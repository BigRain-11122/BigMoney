# -*- coding: utf-8 -*-
"""r914 bm-a rebase prep: intersect incoming origin files vs dirty worktree."""
import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def git(*a):
    return subprocess.run([GIT, "-C", G] + list(a),
                          capture_output=True).stdout.decode("utf-8",
                                                             errors="replace")


incoming = set(git("log", "--name-only", "--format=",
                   "HEAD..origin/main").split())
dirty = set()
for ln in git("status", "--porcelain").splitlines():
    p = ln[3:].strip()
    if p.startswith('"') and p.endswith('"'):
        p = p[1:-1]
    dirty.add(p)
overlap = sorted(dirty & incoming)
print("incoming files=", len(incoming))
print("dirty files=", len(dirty))
print("OVERLAP=", overlap)
