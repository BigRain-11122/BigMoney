# -*- coding: utf-8 -*-
"""r515 bm-c regime probe-3: exact line-ownership mapping of WT tail.
For each WT line after >>>>>>>, find exact matches in stage2/stage3
(with line numbers). Read-only."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
REL = "results/regime_state.json"


def git_show(spec):
    r = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return (r.stdout or b"").decode("utf-8", "replace")


s2 = git_show(":2:" + REL).splitlines()
s3 = git_show(":3:" + REL).splitlines()
s1 = git_show(":1:" + REL).splitlines()
wt = open(os.path.join(ROOT, REL), encoding="utf-8").read().splitlines()

idx2 = {}
for i, l in enumerate(s2, 1):
    idx2.setdefault(l, []).append(i)
idx3 = {}
for i, l in enumerate(s3, 1):
    idx3.setdefault(l, []).append(i)

print("stage line counts: s1=%d s2=%d s3=%d wt=%d" % (len(s1), len(s2), len(s3), len(wt)))
print()
print("=== WT region 1-50 ownership (first 3 marker sections) ===")
for i, l in enumerate(wt[:50], 1):
    m2 = idx2.get(l, [])
    m3 = idx3.get(l, [])
    print("WT-%03d s2=%s s3=%s | %r" % (i, m2, m3, l[:58]))
